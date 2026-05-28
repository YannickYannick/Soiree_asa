from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
import json


class Event(models.Model):
    """Modèle principal pour un événement nightlife"""
    name = models.CharField(max_length=200, default="Afro Night — Édition juin 2026")
    venue = models.CharField(max_length=300, default="La Péniche, 02 quai de la Tournelle, 75005 Paris")
    date = models.DateField()
    capacity = models.PositiveIntegerField(default=300)
    opening_time = models.TimeField(default="23:00")
    closing_time = models.TimeField(default="05:00")
    
    # Contrat venue
    venue_total_ht = models.DecimalField(max_digits=10, decimal_places=2, default=4000)
    venue_total_ttc = models.DecimalField(max_digits=10, decimal_places=2, default=4800)
    venue_deposit = models.DecimalField(max_digits=10, decimal_places=2, default=3000)
    venue_balance = models.DecimalField(max_digits=10, decimal_places=2, default=1800)
    venue_caution = models.DecimalField(max_digits=10, decimal_places=2, default=2000)
    tpe_commission = models.DecimalField(max_digits=5, decimal_places=4, default=0.065)
    sacem_rate = models.DecimalField(max_digits=5, decimal_places=4, default=0.039)
    venue_approval_required = models.BooleanField(default=True)
    venue_approval_received = models.BooleanField(default=False)
    
    # Staff et VIP
    staff_count = models.PositiveIntegerField(default=20)
    vip_invited_count = models.PositiveIntegerField(default=20)
    vip_cost_per_person = models.DecimalField(max_digits=6, decimal_places=2, default=15)
    
    # Dates clés
    deposit_deadline = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.name} - {self.date}"

    @property
    def ticketable_capacity(self):
        """Capacité disponible pour la billetterie (hors staff et VIP)"""
        return self.capacity - self.staff_count - self.vip_invited_count

    @property
    def sacem_amount(self):
        """Montant SACEM fixe basé sur la facture venue TTC"""
        return float(self.venue_total_ttc) * float(self.sacem_rate)

    @property
    def vip_total_cost(self):
        """Coût total des VIP invités"""
        return self.vip_invited_count * float(self.vip_cost_per_person)


class PricingPhase(models.Model):
    """Phase de tarification avec stocks"""
    PHASE_CHOICES = [
        ('seb', 'Super Early Bird'),
        ('eb', 'Early Bird'),
        ('pv', 'Pré-vente'),
        ('lm', 'Last Minute'),
        ('door', 'Sur place'),
    ]
    
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='pricing_phases')
    phase_code = models.CharField(max_length=10, choices=PHASE_CHOICES)
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    
    # Prix
    price_solo = models.DecimalField(max_digits=6, decimal_places=2)
    price_girls_group = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    girls_group_size = models.PositiveIntegerField(default=4)
    price_duo_mixed = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    
    # Prix sur place (uniquement pour phase 'door')
    price_door_23h = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    price_door_00h = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    price_door_after_01h = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    
    # Avantages (stockés en JSON)
    perks = models.JSONField(default=list, blank=True)
    
    # Stocks
    stock_solo = models.PositiveIntegerField(default=0)
    stock_girls_lots = models.PositiveIntegerField(default=0)
    stock_duo_lots = models.PositiveIntegerField(default=0)
    
    # Ventes actuelles
    sold_solo = models.PositiveIntegerField(default=0)
    sold_girls_lots = models.PositiveIntegerField(default=0)
    sold_duo_lots = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['start_date']
        unique_together = ['event', 'phase_code']

    def __str__(self):
        return f"{self.name} ({self.event.name})"

    @property
    def total_places(self):
        """Nombre total de places dans cette phase"""
        return (self.stock_solo + 
                (self.stock_girls_lots * self.girls_group_size) + 
                (self.stock_duo_lots * 2))

    @property
    def sold_places(self):
        """Nombre de places vendues dans cette phase"""
        return (self.sold_solo + 
                (self.sold_girls_lots * self.girls_group_size) + 
                (self.sold_duo_lots * 2))

    @property
    def remaining_places(self):
        """Places restantes"""
        return self.total_places - self.sold_places

    @property
    def fill_percentage(self):
        """Pourcentage de remplissage"""
        if self.total_places == 0:
            return 0
        return round((self.sold_places / self.total_places) * 100, 1)


class VIPTable(models.Model):
    """Table VIP avec formule et commission"""
    FORMULA_CHOICES = [
        (250, '250 € — 4 personnes'),
        (500, '500 € — 5 personnes'),
        (650, '650 € — 5 personnes'),
        (1000, '1 000 € — 5 personnes'),
        (1500, '1 500 € — 5 personnes (VIP unique)'),
    ]
    
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='vip_tables')
    table_number = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    formula = models.PositiveIntegerField(choices=FORMULA_CHOICES, null=True, blank=True)
    double_order = models.BooleanField(default=False, help_text="×2 ressert")
    promo_percent = models.DecimalField(
        max_digits=5, decimal_places=2, 
        default=10,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    promoter_name = models.CharField(max_length=100, blank=True)
    is_booked = models.BooleanField(default=False)

    class Meta:
        ordering = ['table_number']
        unique_together = ['event', 'table_number']

    def __str__(self):
        return f"Table {self.table_number} - {self.event.name}"

    @property
    def included_guests(self):
        """Nombre de personnes incluses selon la formule"""
        if not self.formula:
            return 0
        return 4 if self.formula < 500 else 5

    @property
    def gross_revenue(self):
        """Recette brute (×2 si double order)"""
        if not self.formula:
            return 0
        return self.formula * (2 if self.double_order else 1)

    @property
    def commission_amount(self):
        """Montant de la commission promoteur"""
        return float(self.gross_revenue) * (float(self.promo_percent) / 100)

    @property
    def net_revenue(self):
        """Recette nette après commission"""
        return self.gross_revenue - self.commission_amount

    def save(self, *args, **kwargs):
        # Auto-ajuster la commission par défaut selon la formule
        if self.formula and not self.pk:
            self.promo_percent = 15 if self.formula >= 500 else 10
        super().save(*args, **kwargs)


class BudgetLine(models.Model):
    """Ligne de budget éditable"""
    TIMING_CHOICES = [
        ('avant', 'Avant J'),
        ('nuit', 'Nuit J'),
        ('post', 'Post-soirée'),
    ]
    SECTION_CHOICES = [
        ('revenue', 'Recettes'),
        ('fixed', 'Dépenses fixes'),
        ('human', 'Dépenses humaines'),
    ]
    
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='budget_lines')
    name = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    timing = models.CharField(max_length=10, choices=TIMING_CHOICES, default='avant')
    section = models.CharField(max_length=10, choices=SECTION_CHOICES)
    is_calculated = models.BooleanField(default=False, help_text="Calculé automatiquement")
    is_optional = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['section', 'order', 'name']

    def __str__(self):
        return f"{self.name}: {self.amount}€"


class InstagramPost(models.Model):
    """Publication Instagram planifiée"""
    TYPE_CHOICES = [
        ('Post', 'Post (feed)'),
        ('Reel', 'Reel (vidéo)'),
        ('Story', 'Story (éphémère)'),
    ]
    STATUS_CHOICES = [
        ('draft', 'Brouillon'),
        ('pending_approval', 'En attente accord venue'),
        ('approved', 'Approuvé'),
        ('published', 'Publié'),
    ]
    
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='instagram_posts')
    scheduled_date = models.DateField()
    days_before = models.IntegerField(help_text="J-x avant l'événement")
    phase = models.CharField(max_length=50)
    post_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    title = models.CharField(max_length=200)
    content = models.TextField()
    cta = models.CharField(max_length=300, verbose_name="Call to Action")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending_approval')
    venue_approval_required = models.BooleanField(default=True)

    class Meta:
        ordering = ['scheduled_date']

    def __str__(self):
        return f"J-{self.days_before}: {self.title}"

    @property
    def is_locked(self):
        """La publication est verrouillée si l'accord venue n'est pas reçu"""
        return self.venue_approval_required and self.status == 'pending_approval'


class TicketSale(models.Model):
    """Vente de billet pour le tracking"""
    GENDER_CHOICES = [
        ('F', 'Femme'),
        ('M', 'Homme'),
    ]
    TICKET_TYPE_CHOICES = [
        ('solo', 'Solo'),
        ('girls_group', 'Groupe filles'),
        ('duo_mixed', 'Duo mixte'),
    ]
    
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='ticket_sales')
    pricing_phase = models.ForeignKey(PricingPhase, on_delete=models.CASCADE, related_name='sales')
    sale_date = models.DateField()
    ticket_type = models.CharField(max_length=20, choices=TICKET_TYPE_CHOICES)
    quantity = models.PositiveIntegerField(default=1)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    amount = models.DecimalField(max_digits=8, decimal_places=2)

    class Meta:
        ordering = ['sale_date']

    def __str__(self):
        return f"{self.sale_date} - {self.ticket_type} x{self.quantity}"


class SimulationScenario(models.Model):
    """Scénario de simulation financière"""
    SCENARIO_CHOICES = [
        ('pessimistic', 'Pessimiste'),
        ('neutral', 'Neutre'),
        ('optimistic', 'Optimiste'),
    ]
    
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='scenarios')
    scenario_type = models.CharField(max_length=20, choices=SCENARIO_CHOICES)
    
    # Paramètres de simulation
    total_pax = models.PositiveIntegerField(default=200)
    bar_spend_per_person = models.DecimalField(max_digits=6, decimal_places=2, default=25)
    tpe_percent = models.DecimalField(
        max_digits=5, decimal_places=2, 
        default=60,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    alcohol_cost = models.DecimalField(max_digits=10, decimal_places=2, default=2000)
    
    # Résultats calculés (mis à jour automatiquement)
    total_revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_expenses = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_result = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    margin_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    class Meta:
        unique_together = ['event', 'scenario_type']

    def __str__(self):
        return f"{self.get_scenario_type_display()} - {self.event.name}"

    def calculate_results(self):
        """Calcule les résultats de la simulation"""
        event = self.event
        
        # Recettes entrées (estimation basée sur le mix de phases)
        ticket_revenue = self.total_pax * 15  # Prix moyen estimé
        
        # Recettes tables
        tables_net = sum(t.net_revenue for t in event.vip_tables.filter(is_booked=True))
        tables_pax = sum(t.included_guests for t in event.vip_tables.filter(is_booked=True))
        
        # Recettes bar (après commission TPE)
        paying_pax = self.total_pax - event.staff_count - tables_pax
        bar_gross = paying_pax * float(self.bar_spend_per_person)
        bar_tpe_amount = bar_gross * (float(self.tpe_percent) / 100)
        bar_commission = bar_tpe_amount * float(event.tpe_commission)
        bar_net = bar_gross - bar_commission
        
        self.total_revenue = ticket_revenue + tables_net + bar_net
        
        # Dépenses
        fixed_expenses = sum(
            float(b.amount) for b in event.budget_lines.filter(section='fixed')
        )
        human_expenses = sum(
            float(b.amount) for b in event.budget_lines.filter(section='human')
        )
        self.total_expenses = fixed_expenses + human_expenses + float(self.alcohol_cost)
        
        self.net_result = self.total_revenue - self.total_expenses
        
        if self.total_revenue > 0:
            self.margin_percent = (self.net_result / self.total_revenue) * 100
        else:
            self.margin_percent = 0
        
        self.save()
