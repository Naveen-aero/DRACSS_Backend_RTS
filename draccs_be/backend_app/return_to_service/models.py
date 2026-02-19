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
    #  INTRACK (shipment going to service center)
    # =========================================================
    intrack_shipping_date = models.DateField(blank=True, null=True)
    intrack_courier = models.CharField(max_length=150, blank=True, null=True)
    intrack_expected_date = models.DateField(blank=True, null=True)
    intrack_tracking_id = models.CharField(max_length=150, blank=True, null=True)
    intrack_status = models.CharField(max_length=80, blank=True, null=True)
    intrack_photo = models.ImageField(upload_to="rtb/intrack/", blank=True, null=True)
    intrack_remarks = models.TextField(blank=True, null=True)

    # =========================================================
    #  OUTTRACK (shipment returning back to customer)
    # =========================================================
    outtrack_shipping_date = models.DateField(blank=True, null=True)
    outtrack_courier = models.CharField(max_length=150, blank=True, null=True)
    outtrack_expected_date = models.DateField(blank=True, null=True)
    outtrack_tracking_id = models.CharField(max_length=150, blank=True, null=True)
    outtrack_status = models.CharField(max_length=80, blank=True, null=True)
    outtrack_photo = models.ImageField(upload_to="rtb/outtrack/", blank=True, null=True)
    outtrack_remarks = models.TextField(blank=True, null=True)

    # =========================================================
    #  Technician assignment
    # =========================================================
    assigned_technician_id = models.CharField(max_length=10,blank=True,null=True)
    assigned_technician = models.TextField(blank=True, null=True)
    assigned_employee_id = models.CharField(
        max_length=10,
        unique=True,
        blank=True,
        null=True
    )
    assigned_remarks = models.CharField(max_length=1000, null=True)

    # --- System fields ---
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "rtb_service_requests"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.uas_model} | {self.flight_controller} | {self.date_of_occurrence}"


#  NEW MODEL (Added) - Multiple components per RTB request
class RTBServiceRequestComponent(models.Model):
    rtb_request = models.ForeignKey(
        ReturnToBaseServiceRequest,
        related_name="components",          #  this will appear as "components" in API
        on_delete=models.CASCADE
    )

    component_type = models.CharField(max_length=200)  # e.g., Water Tube, Screws
    quantity = models.PositiveIntegerField(default=1)  # e.g., 3, 25
    remarks = models.TextField(blank=True, null=True)  # optional

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "rtb_service_request_components"
        ordering = ["-created_at"]

    def __str__(self):
        return f"RTB#{self.rtb_request_id} | {self.component_type} | Qty:{self.quantity}"