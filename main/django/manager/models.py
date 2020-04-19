from django.db import models
 
class Stock(models.Model):

    # –Á•¿
    brand = models.CharField(max_length=128)
    # •]‰¿Šz
    valuation = models.IntegerField()
    
    
    

