from django.db import models
 
class Stock(models.Model):

    # ����
    brand = models.CharField(max_length=128)
    # �]���z
    valuation = models.IntegerField()
    
    
    

