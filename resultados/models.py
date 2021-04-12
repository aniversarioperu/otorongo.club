from django.db import models


class Department(models.Model):
    ubigeo = models.CharField(max_length=200, null=True)
    name = models.TextField()


class Province(models.Model):
    ubigeo = models.CharField(max_length=200)
    name = models.TextField()


class District(models.Model):
    ubigeo = models.CharField(max_length=200)
    name = models.TextField()


class Local(models.Model):
    name = models.TextField()
    address = models.ForeignKey('Address', null=True, on_delete=models.SET_NULL)
    department = models.ForeignKey(Department, null=True, on_delete=models.SET_NULL)
    province = models.ForeignKey(Province, null=True, on_delete=models.SET_NULL)
    district = models.ForeignKey(District, null=True, on_delete=models.SET_NULL)

    class Meta:
        unique_together = [
            'name', 'address', 'department', 'province', 'district'
        ]


class Address(models.Model):
    name = models.TextField()


class Party(models.Model):
    name = models.TextField()


class Votacion(models.Model):
    party = models.ForeignKey(Party, on_delete=models.SET_NULL, null=True)
    votes = models.IntegerField()


class ActaType(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=200, null=True)


class ActaStatus(models.Model):
    name = models.CharField(max_length=200)


class Acta(models.Model):
    mesa_numero = models.CharField(max_length=200)
    copia_numero = models.CharField(max_length=200)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    province = models.ForeignKey(Province, on_delete=models.SET_NULL, null=True)
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True)
    local = models.ForeignKey(Local, on_delete=models.SET_NULL, null=True)
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True)
    habiles = models.IntegerField(null=True)
    votantes = models.IntegerField(null=True)
    status = models.ForeignKey(ActaStatus, on_delete=models.SET_NULL, null=True)
    blanco = models.IntegerField(null=True)
    nulo = models.IntegerField(null=True)
    impugnado = models.IntegerField(null=True)
    total_votos = models.IntegerField(null=True)
    votaciones = models.ManyToManyField(Votacion)
    acta_type = models.ForeignKey(ActaType, on_delete=models.SET_NULL, null=True)
