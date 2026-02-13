from django.db import models


class ReturnToBaseServiceRequest(models.Model):
    # --- Form fields ---
    uas_model = models.CharField(max_length=100)  # e.g., Bhumi A10E
    flight_controller = models.CharField(max_length=100)  # e.g., Cube Orange

    # You gave 3 serial-like numbers; store all 3 separately
    serial_number = models.CharField(max_length=100)

    date_of_occurrence = models.DateField()

    # Not provided in your sample, but field exists in form
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

    # --- System fields ---
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "rtb_service_requests"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.uas_model} | {self.flight_controller} | {self.date_of_occurrence}"