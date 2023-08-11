from django.db import models
from django.utils.timezone import now
from django.core import serializers
import uuid
import json

# Create your models here.

# <HINT> Create a Car Make model `class CarMake(models.Model)`:
# - Name
# - Description
# - Any other fields you would like to include in car make model
# - __str__ method to print a car make object
class CarMake(models.Model):
    name = models.CharField(null=False, max_length=100, default='')
    description = models.CharField(max_length=2000, null=True)

    def __str__(self):
        return self.name + "\n" + self.description 

# <HINT> Create a Car Model model `class CarModel(models.Model):`:
# - Many-To-One relationship to Car Make model (One Car Make has many Car Models, using ForeignKey field)
# - Name
# - Dealer id, used to refer a dealer created in cloudant database
# - Type (CharField with a choices argument to provide limited choices such as Sedan, SUV, WAGON, etc.)
# - Year (DateField)
# - Any other fields you would like to include in car model
# - __str__ method to print a car make object
class CarModel(models.Model):
    make = models.ForeignKey(CarMake, null=True, on_delete=models.CASCADE)
    name = models.CharField(null=False, max_length=20, default='')
    dealer_id = models.IntegerField(default=1, primary_key=True)

    SEDAN = 'Sedan'
    SUV = 'SUV'
    WAGON = 'Wagon'
    type_choices = [
        (SEDAN, 'Sedan'),
        (SUV, 'SUV'),
        (WAGON, 'Wagon'),
    ]

    car_type = models.CharField(null=False, max_length=20, choices=type_choices, default=SEDAN)
    year = models.DateField(null=True)

    def __str__(self):
        return "Model: " + self.name + "\nType: " + self.car_type + "\nYear: " + self.year.strftime('%Y')


# <HINT> Create a plain Python class `CarDealer` to hold dealer data
class CarDealer:
    def __init__(self, address, city, name, id_, lat, long_, short_name, st, zip_):
        self.address = address
        self.city = city
        self.name = name
        self.id_ = id_
        self.lat = lat
        self.long_ = long_
        self.short_name = short_name
        self.st = st
        self.zip_ = zip_
    
    def __str__(self):
        return "Dealer name: " + self.name

# <HINT> Create a plain Python class `DealerReview` to hold review data
class DealerReview:
    def __init__(self, dealership, name, purchase, review):
        self.dealership = dealership
        self.id_ = None
        self.name = name 
        self.purchase = purchase
        self.review = review 
        self.purchase_date = None
        self.car_make = None
        self.car_model = None
        self.car_year = None
        self.sentiment = None
    
    def __str__(self):
        return self.car_make + " " + self.car_model + " " + self.name

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
