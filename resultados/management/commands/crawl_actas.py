from random import randint
from time import sleep
import requests

from parsel import Selector
from django.core.management.base import BaseCommand

from resultados.models import ActaStatus, Department, Province, District, Acta, Local, Address, \
    ActaType, Party, Votacion

MAX_RETRIES = 5

BASE_URL = 'https://www.web.onpe.gob.pe/modElecciones/elecciones/elecciones2016/PRPCP2016/ajax.php'
DEPARTMENTS = [
    '010000',
    '020000',
    '030000',
    '040000',
    '050000',
    '060000',
    '240000',
    '070000',
    '080000',
    '090000',
    '100000',
    '110000',
    '120000',
    '130000',
    '140000',
    '150000',
    '160000',
    '170000',
    '180000',
    '190000',
    '200000',
    '210000',
    '220000',
    '230000',
    '250000',
]


def get_session():
    sleep(1)
    s = requests.Session()
    s.headers.update({
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
        'Origin': 'https://resultados.eleccionescongresales2020.pe',
        'X-Requested-With': 'XMLHttpRequest'
    })
    return s

SESSION = get_session()


def get_departments():
    sleep(randint(0, 2))
    payload = {
        'pid': '6233258373950512',
        '_clase': 'ubigeo',
        '_accion': 'getDepartamentos',
        'dep_id': '',
        'tipoElec': '10',
        'tipoC': '',
        'modElec': '',
        'ambito': 'P',
        'pantalla': ''
    }
    res = SESSION.post(BASE_URL, data=payload)
    sel = Selector(res.text)
    departments = sel.xpath('//option')

    for i in departments:
        value = i.xpath('@value').extract_first()
        if not value:
            continue

        name = i.xpath('text()').extract_first()
        dept, _ = Department.objects.get_or_create(
            ubigeo=value, name=name
        )

    departments = sel.xpath('//option/@value')
    return extract_items(departments)


def extract_items(results):
    out = []
    for result in results:
        if results == "-1?-1":
            continue
        if result:
            out.append(result.extract())
    return out


def get_provinces(department):
    sleep(randint(0, 2))
    payload = {
        'pid': '6233258373950512',
        '_clase': 'ubigeo',
        '_accion': 'getProvincias',
        'tipoElec': '10',
        'modElec': '',
        'dep_id': department,
        'pantalla': ''
    }
    res = SESSION.post(BASE_URL, data=payload)
    sel = Selector(res.text)
    provinces = sel.xpath('//option')

    for i in provinces:
        value = i.xpath('@value').extract_first()
        if not value:
            continue

        name = i.xpath('text()').extract_first()
        Province.objects.get_or_create(
            ubigeo=value, name=name
        )

    provinces = sel.xpath('//option/@value')
    return extract_items(provinces)


def get_district(ubigeo):
    sleep(randint(0, 2))
    payload = {
        'pid': '6233258373950512',
        '_clase': 'ubigeo',
        '_accion': 'getDistritos',
        'prov_id': ubigeo,
        'tipoElec': '10',
        'modElec': '',
        'pantalla': ''
    }
    res = SESSION.post(BASE_URL, data=payload)
    sel = Selector(res.text)
    districts = sel.xpath('//option')

    for i in districts:
        value = i.xpath('@value').extract_first()
        if not value:
            continue

        name = i.xpath('text()').extract_first()
        District.objects.get_or_create(
            ubigeo=value, name=name
        )

    districts = sel.xpath('//option/@value')
    return extract_items(districts)


def get_locales(ubigeo):
    """Returns list of acta number and ubigeo local

    returns [
     '3073?140124',
     '5365?140124',
     '3071?140124',
     '3072?140124',
     '3074?140124',
     '3070?140124',
     '3075?140124',
     '3076?140124'
    ]
    """
    sleep(randint(0, 2))
    payload = {
    'pid': '6233258373950512',
        '_clase': 'actas',
        '_accion': 'getLocalesVotacion',
        'tipoElec': '',
        'ubigeo': ubigeo
    }
    res = SESSION.post(BASE_URL, data=payload)
    sel = Selector(res.text)
    locales = sel.xpath('//option/@value')
    return extract_items(locales)


def get_acta_numeros(local):
    sleep(randint(0, 2))
    payload = {
        'pid': '6233258373950512',
        '_clase': 'actas',
        '_accion': 'displayActas',
        'tipoElec': '',
        'ubigeo': local.split('?')[1],
        'actasPor': local.split('?')[0],
        'ubigeoLocal': local.split('?')[1],
        'page': 'undefined',
    }
    res = SESSION.post(BASE_URL, data=payload)
    sel = Selector(res.text)
    actas = sel.xpath('//a/text()').extract()

    out = []
    for acta in actas:
        if acta != '1':
            out.append(acta)
    return out


def download_acta(ubigeo, mesa_numero, acta_type_code, department, province, district):
    acta_type = ActaType.objects.get(code=acta_type_code)
    sleep(randint(0, 2))
    payload = {
        'pid': '6233258373950512',
        '_clase': 'mesas',
        '_accion': 'displayMesas',
        'ubigeo': ubigeo,
        'nroMesa': mesa_numero,
        'tipoElec': acta_type_code,
        'page': 1,
        'pornumero': '1',
    }
    res = SESSION.post(BASE_URL, data=payload)
    with open('/Users/carlosp420/Downloads/a.html', 'w') as handle:
        handle.write(res.text)

    sel = Selector(res.text)
    mesa_numero, copia_numero = sel.xpath('//table[@class="table13"]/tbody/tr/td/text()').extract()
    copia_numero = copia_numero.strip()

    local, address = sel.xpath('//table[@class="table14"]/tbody/tr[2]/td/text()').extract()
    habiles, votantes, status = sel.xpath('//table[@class="table15"]/tbody/tr[2]/td/text()').extract()

    acta, _ = Acta.objects.get_or_create(
        mesa_numero=mesa_numero,
        copia_numero=copia_numero,
    )

    department_obj, _ = Department.objects.get_or_create(name=department)
    province_obj, _ = Province.objects.get_or_create(name=province)
    district_obj, _ = District.objects.get_or_create(name=district)
    status_obj, _ = ActaStatus.objects.get_or_create(name=status.strip())
    address_obj, _ = Address.objects.get_or_create(name=address)
    local_obj, _ = Local.objects.get_or_create(
        name=local,
        address=address_obj,
        department=department_obj,
        province=province_obj,
        district=district_obj
    )

    acta.department = department_obj
    acta.province = province_obj
    acta.district = district_obj
    acta.local = local_obj
    acta.address = address_obj
    acta.habiles = habiles.strip()
    acta.votantes = votantes.strip()
    acta.status = status_obj
    acta.acta_type = acta_type
    acta.save()

    rows = sel.xpath('//table[@class="table06"]/tbody/tr')

    for row in rows[1:-4]:
        party_votes = row.xpath('.//td/text()').extract()
        if not party_votes:
            continue

        party, votes = party_votes
        votes = votes.strip()
        party_obj, _ = Party.objects.get_or_create(name=party)
        votacion, _ = Votacion.objects.get_or_create(party=party_obj, votes=votes)
        acta.votaciones.add(votacion)

    _, number = rows[-4].xpath('.//td/text()').extract()
    acta.blanco = number.strip()

    _, number = rows[-3].xpath('.//td/text()').extract()
    acta.nulo = number.strip()

    _, number = rows[-2].xpath('.//td/text()').extract()
    acta.impugnado = number.strip()

    _, number = rows[-1].xpath('.//td/text()').extract()
    acta.total_votos = number.strip()

    acta.save()
    return acta


def crawl():
    acta_type, _ = ActaType.objects.get_or_create(
        code='10', name='PRESIDENCIAL'
    )
    departments = get_departments()

    for department in departments:
        provinces = get_provinces(department)

        for province in provinces:
            districts = get_district(province)

            for district in districts:
                locales = get_locales(district)

                for local in locales:
                    actas = get_acta_numeros(local)

                    for acta in actas:
                        print(local, acta)
                        res = download_acta(local, acta, acta_type.code, department, province, district)
                        print(f'downloaded {res}')


class Command(BaseCommand):
    def handle(self, *args, **options):
        crawl()
