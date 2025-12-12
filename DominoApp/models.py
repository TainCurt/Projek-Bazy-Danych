from itertools import chain
from pyexpat import model
import time
from django.db import models
from django.utils import timezone

class UserRole(models.TextChoices):
    ADMIN = 'ADMIN', 'Administrator'
    RESIDENT = 'RESIDENT', 'Mieszkaniec'

class ReportType(models.TextChoices):
    FLAT = 'FLAT', 'Mieszkanie'
    BUILDING = 'BUILDING', 'Budynek'
    GENERAL = 'GENERAL', 'Ogólne'

class ReportStatus(models.TextChoices):
    DONE = 'DONE', 'Wykonane'
    ABANDONED = 'ABANDONED', 'Porzucone'
    WAITING = 'WAITING', 'Oczekujące'

class UserFlatRole(models.TextChoices):
    OWNER = 'OWNER', 'Właściciel'
    TENANT = 'TENANT', ' Najemca'

class RentStatus(models.TextChoices):
    PAID = 'PAID', 'Zapłacone'
    PENDING = 'PENDING', 'Oczekujące'

class Building(models.Model):
    BuildingId = models.BigAutoField(primary_key=True)
    BuildingStreet = models.CharField(max_length=30)
    BuildingNumber = models.CharField(max_length=10)
    BuildingCity = models.CharField(max_length=50)
    BuildingPostal = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.BuildingStreet} {self.BuildingNumber} {self.BuildingCity}"

class Flat(models.Model):
    FlatId = models.BigAutoField(primary_key=True)
    BuildingId = models.ForeignKey(Building, on_delete=models.CASCADE, related_name='flats')
    FlatNumber = models.CharField(max_length=10)
    FlatFloor = models.SmallIntegerField()
    FlatArea = models.DecimalField(max_digits=6, decimal_places=2)
    FlatStatus = models.BooleanField(default=True)

    def __str__(self):
        return f"Flat {self.FlatNumber} (Floor {self.FlatFloor} in {self.BuildingId})"
    



class User(models.Model):
    UserId = models.BigAutoField(primary_key=True)
    UserName = models.CharField(max_length=30)
    UserSurname = models.CharField(max_length=40)
    UserEmail = models.CharField(max_length=100, unique=True)
    UserPassword = models.CharField(max_length=128)
    UserRole = models.CharField(max_length=10, choices=UserRole.choices)
    UserDate = models.DateField(auto_now_add=True)
    UserStatus = models.BooleanField(default=True)
    Flats = models.ManyToManyField(Flat, through='UserFlat', related_name='users' )

    def __str__(self):
        return f"{self.UserName} {self.UserSurname} ({self.UserRole})"



class UserFlat(models.Model):
    UserFlatId = models.BigAutoField(primary_key=True)
    UserId = models.ForeignKey(User, on_delete=models.CASCADE, related_name='userflats')
    FlatId = models.ForeignKey(Flat, on_delete=models.CASCADE, related_name='userflats')
    UserFlatDateFrom = models.DateField(auto_now_add=True)
    UserFlatDateTo = models.DateField(null=True, blank=True)
    UserFlatRole = models.CharField(max_length=10, choices=UserFlatRole.choices)
    class Meta:
        unique_together = ('UserId', 'FlatId', 'UserFlatDateFrom')

    def __str__(self):
        return f"{self.UserId} - {self.FlatId}"


class Rent(models.Model):
    RentId = models.BigAutoField(primary_key=True)
    FlatId = models.ForeignKey(Flat, on_delete=models.CASCADE, related_name='rents')
    RentMonth = models.SmallIntegerField()
    RentYear = models.SmallIntegerField()
    RentAmount = models.DecimalField(max_digits=12,  decimal_places=2)
    RentDateDue = models.DateField()
    RentStatus = models.CharField(max_length=10, choices=RentStatus.choices, default=RentStatus.PENDING)
    RentDate = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.RentMonth}/{self.RentYear} - {self.RentAmount}"



class Report(models.Model):
    ReportId = models.BigAutoField(primary_key=True)
    UserId = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports')
    FlatId = models.ForeignKey(Flat, on_delete=models.CASCADE, null=True, blank=True)
    BuildingId = models.ForeignKey(Building, on_delete=models.CASCADE, null=True, blank=True)
    ReportType = models.CharField(max_length=10, choices=ReportType.choices, default=ReportType.GENERAL)
    ReportTitle = models.CharField(max_length=100)
    ReportDescription = models.TextField()
    ReportCategory = models.CharField(max_length=500)
    ReportStatus = models.CharField(max_length=15, choices=ReportStatus.choices, default=ReportStatus.WAITING)
    ReportTime = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.ReportStatus} ({self.ReportStatus})"


class Announ(models.Model):
    AnnounId = models.BigAutoField(primary_key=True)
    UserId = models.ForeignKey(User, on_delete=models.CASCADE, related_name='announs')
    AnnounTitle = models.CharField(max_length=100)
    AnnounDescription = models.TextField()
    AnnounDate = models.DateTimeField(default=timezone.now)
    AnnounFrom = models.DateField()
    AnnounTo = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.AnnounTitle} ({self.AnnounFrom} - {self.AnnounTo})"
    
class AuthToken(models.Model):
    TokenId = models.BigAutoField(primary_key=True)
    UserId = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tokens')
    TokenKey = models.CharField(max_length=40, unique=True)
    TokenCreated = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.UserId.UserEmail} ({self.TokenCreated})"

    

