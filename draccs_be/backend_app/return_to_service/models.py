# from django.db import models


# class ReturnToBaseServiceRequest(models.Model):
#     # --- Form fields ---
#     uas_model = models.CharField(max_length=100)  # e.g., Bhumi A10E
#     flight_controller = models.CharField(max_length=100)  # e.g., Cube Orange

#     # You gave 3 serial-like numbers; store all 3 separately
#     serial_number = models.CharField(max_length=100)

#     date_of_occurrence = models.DateField()

#     # Not provided in your sample, but field exists in form
#     total_accumulated_hours = models.DecimalField(
#         max_digits=10, decimal_places=2, blank=True, null=True
#     )

#     description_of_difficulty = models.TextField()  # "Pump not working"
#     affected_subsystem_component = models.CharField(max_length=200)  # "5L -V1 Pump"
#     symptoms_observed = models.TextField()  # "No suction from the pump"
#     environmental_conditions = models.CharField(max_length=200)  # "Normal"
#     operator_actions_taken = models.TextField()  # "Pheumatic cleaning"
#     immediate_consequence_flight_outcome = models.TextField()
#     corrective_actions_taken = models.TextField()  # "Inspected for any blockage"

#     reported_by = models.CharField(max_length=150)  # "Beautus(Client)"
#     reported_date = models.DateField()
#     remarks = models.TextField(blank=True, null=True)

#     # --- System fields ---
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         db_table = "rtb_service_requests"
#         ordering = ["-created_at"]

#     def __str__(self):
#         return f"{self.uas_model} | {self.flight_controller} | {self.date_of_occurrence}"


from django.db import models


class ReturnToBaseServiceRequest(models.Model):
    # --- Form fields ---
    uas_model = models.CharField(max_length=100)  # e.g., Bhumi A10E
    flight_controller = models.CharField(max_length=100)  # e.g., Cube Orange

    serial_number = models.CharField(max_length=100)

    date_of_occurrence = models.DateField()

    total_accumulated_hours = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )

    description_of_difficulty = models.TextField()  # "Pump not working"
    affected_subsystem_component = models.CharField(max_length=200)  # "5L -V1 Pump"
    symptoms_observed = models.TextField()  # "No suction from the pump"
    environmental_conditions = models.CharField(max_length=200)  # "Normal"
    operator_actions_taken = models.TextField()  # "Pheumatic cleaning"
    immediate_consequence_flight_outcome = models.TextField()
    corrective_actions_taken = models.TextField()  # "Inspected for any blockage"

    reported_by = models.CharField(max_length=150)  # "Beautus(Client)"
    reported_date = models.DateField()
    remarks = models.TextField(blank=True, null=True)

    # =========================================================
    #  NEW: INTRACK (shipment going to service center)
    # =========================================================
    intrack_shipping_date = models.DateField(blank=True, null=True)
    intrack_courier = models.CharField(max_length=150, blank=True, null=True)
    intrack_expected_date = models.DateField(blank=True, null=True)
    intrack_tracking_id = models.CharField(max_length=150, blank=True, null=True)
    intrack_status = models.CharField(max_length=80, blank=True, null=True)
    intrack_photo = models.ImageField(upload_to="rtb/intrack/", blank=True, null=True)
    intrack_remarks = models.TextField(blank=True, null=True)

    # =========================================================
    #  NEW: OUTTRACK (shipment returning back to customer)
    # =========================================================
    outtrack_shipping_date = models.DateField(blank=True, null=True)
    outtrack_courier = models.CharField(max_length=150, blank=True, null=True)
    outtrack_expected_date = models.DateField(blank=True, null=True)
    outtrack_tracking_id = models.CharField(max_length=150, blank=True, null=True)
    outtrack_status = models.CharField(max_length=80, blank=True, null=True)
    outtrack_photo = models.ImageField(upload_to="rtb/outtrack/", blank=True, null=True)
    outtrack_remarks = models.TextField(blank=True, null=True)

    # --- System fields ---
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "rtb_service_requests"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.uas_model} | {self.flight_controller} | {self.date_of_occurrence}"