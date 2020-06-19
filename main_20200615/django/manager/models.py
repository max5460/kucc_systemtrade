from django.db import models

class Stock(models.Model):
    brand_code = models.CharField(db_column='BRAND_CODE', primary_key=True, max_length=10)  # Field name made lowercase.
    brand_desc = models.TextField(db_column='BRAND_DESC', blank=True, null=True)  # Field name made lowercase.
    prediction = models.CharField(db_column='PREDICTION', max_length=2, blank=True, null=True)  # Field name made lowercase.
    accuracy = models.DecimalField(db_column='ACCURACY', max_digits=10, decimal_places=7, blank=True, null=True)  # Field name made lowercase.
    training_data_count = models.IntegerField(db_column='TRAINING_DATA_COUNT', blank=True, null=True)  # Field name made lowercase.
    predict_date = models.DateTimeField(db_column='PREDICT_DATE', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'PREDICT_RESULT'