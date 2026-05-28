"""Views for events app."""

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.utils import timezone
from datetime import datetime, timedelta, date
from decimal import Decimal
import json

from .models import (
    Event, PricingPhase, VIPTable, BudgetLine, 
    InstagramPost, TicketSale, SimulationScenario
)


def get_or_create_default_event():
    """Crée un événement par défaut si aucun n'existe."""
    event = Event.objects.first()
    if not event:
        event = Event.objects.create(
            name="Afro Night — Édition juin 2026",
            venue="La Péniche, 02 quai de la Tournelle, 75005 Paris",
            date=date(2026, 6, 20),
            capacity=300,
        )
        create_default_data(event)
    return event


def create_default_data(event):
    """Crée les données par défaut pour un nouvel événement."""
    event_date = event.date
    
    # Phases de pricing
    phases_data = [
        {
            'phase_code': 'seb',
            'name': 'Super Early Bird',
            'start_offset': -24,
            'end_offset': -18,
            'price_solo': 10,
            'price_girls_group': 10,
            'price_duo_mixed': None,
            'perks': ['Shot offert', 'Photo booth'],
            'stock_solo': 30,
            'stock_girls_lots': 5,
            'stock_duo_lots': 0,
        },
        {
            'phase_code': 'eb',
            'name': 'Early Bird',
            'start_offset': -17,
            'end_offset': -11,
            'price_solo': 13,
            'price_girls_group': 10,
            'price_duo_mixed': 22,
            'perks': ['Cocktail offert avant 00h30'],
            'stock_solo': 45,
            'stock_girls_lots': 6,
            'stock_duo_lots': 4,
        },
        {
            'phase_code': 'pv',
            'name': 'Pré-vente',
            'start_offset': -10,
            'end_offset': -5,
            'price_solo': 16,
            'price_girls_group': 12,
            'price_duo_mixed': 28,
            'perks': ['Fast track file d\'attente'],
            'stock_solo': 40,
            'stock_girls_lots': 4,
            'stock_duo_lots': 3,
        },
        {
            'phase_code': 'lm',
            'name': 'Last Minute',
            'start_offset': -4,
            'end_offset': -1,
            'price_solo': 18,
            'price_girls_group': 14,
            'price_duo_mixed': None,
            'perks': [],
            'stock_solo': 13,
            'stock_girls_lots': 3,
            'stock_duo_lots': 0,
        },
        {
            'phase_code': 'door',
            'name': 'Sur place',
            'start_offset': 0,
            'end_offset': 0,
            'price_solo': 18,
            'price_girls_group': None,
            'price_duo_mixed': None,
            'price_door_23h': 18,
            'price_door_00h': 20,
            'price_door_after_01h': 22,
            'perks': [],
            'stock_solo': 6,
            'stock_girls_lots': 0,
            'stock_duo_lots': 0,
        },
    ]
    
    for data in phases_data:
        PricingPhase.objects.create(
            event=event,
            phase_code=data['phase_code'],
            name=data['name'],
            start_date=event_date + timedelta(days=data['start_offset']),
            end_date=event_date + timedelta(days=data['end_offset']),
            price_solo=data['price_solo'],
            price_girls_group=data.get('price_girls_group'),
            price_duo_mixed=data.get('price_duo_mixed'),
            price_door_23h=data.get('price_door_23h'),
            price_door_00h=data.get('price_door_00h'),
            price_door_after_01h=data.get('price_door_after_01h'),
            perks=data['perks'],
            stock_solo=data['stock_solo'],
            stock_girls_lots=data['stock_girls_lots'],
            stock_duo_lots=data['stock_duo_lots'],
        )
    
    # Tables VIP (10 slots)
    for i in range(1, 11):
        VIPTable.objects.create(
            event=event,
            table_number=i,
            formula=None,
            is_booked=False,
        )
    
    # Budget par défaut
    budget_data = [
        # Dépenses fixes - Avant J
        {'name': 'La Péniche - Dépôt', 'amount': 3000, 'timing': 'avant', 'section': 'fixed', 'order': 1},
        {'name': 'La Péniche - Solde', 'amount': 1800, 'timing': 'avant', 'section': 'fixed', 'order': 2},
        {'name': 'Assurance RC Organisateur', 'amount': 150, 'timing': 'avant', 'section': 'fixed', 'order': 3},
        {'name': 'Communication / flyers', 'amount': 1000, 'timing': 'avant', 'section': 'fixed', 'order': 4},
        {'name': 'Mobilier VIP / déco', 'amount': 800, 'timing': 'avant', 'section': 'fixed', 'order': 5},
        {'name': 'Camion / transport', 'amount': 200, 'timing': 'avant', 'section': 'fixed', 'order': 6},
        # Dépenses fixes - Nuit J
        {'name': 'Alcool & softs (dépôt-vente)', 'amount': 2000, 'timing': 'nuit', 'section': 'fixed', 'order': 7},
        {'name': 'VIP invités (20 × 15 €)', 'amount': 300, 'timing': 'nuit', 'section': 'fixed', 'order': 8},
        # Dépenses humaines - Post
        {'name': 'DJ', 'amount': 800, 'timing': 'post', 'section': 'human', 'order': 1},
        {'name': 'Sécurité extra (2 agents)', 'amount': 400, 'timing': 'post', 'section': 'human', 'order': 2},
        {'name': 'Barman', 'amount': 200, 'timing': 'post', 'section': 'human', 'order': 3},
        {'name': 'SACEM (3,9 % × 4 800 €)', 'amount': 187, 'timing': 'post', 'section': 'human', 'order': 4, 'is_calculated': True},
        {'name': 'Photographe', 'amount': 500, 'timing': 'post', 'section': 'human', 'order': 5, 'is_optional': True},
        {'name': 'Ingénieur son', 'amount': 0, 'timing': 'post', 'section': 'human', 'order': 6, 'is_optional': True},
        {'name': 'Performeuses', 'amount': 0, 'timing': 'post', 'section': 'human', 'order': 7, 'is_optional': True},
    ]
    
    for data in budget_data:
        BudgetLine.objects.create(
            event=event,
            **data
        )
    
    # Publications Instagram
    instagram_data = [
        {'days': -24, 'phase': 'Super EB', 'type': 'Post', 'title': 'Save the date 🔒', 
         'content': 'Date + lieu + genres musicaux + billetterie ouverte', 'cta': 'Story countdown + lien bio'},
        {'days': -22, 'phase': 'Super EB', 'type': 'Reel', 'title': 'Teaser ambiance',
         'content': 'Montage 30s clips foule/danse/lumières + musique amapiano', 'cta': '"Tag ton équipe"'},
        {'days': -19, 'phase': 'Super EB', 'type': 'Story', 'title': 'Urgence Super EB ⚡',
         'content': '"48h restantes à 10 € — après-demain 13 €"', 'cta': 'Swipe-up billetterie'},
        {'days': -17, 'phase': 'Early Bird', 'type': 'Post', 'title': 'Girls Deal 👯‍♀️',
         'content': '"4 filles = 10 € + cocktail · 6 lots seulement · hommes paient 13 €"', 'cta': '"Taguez vos 3 meilleures amies"'},
        {'days': -15, 'phase': 'Early Bird', 'type': 'Reel', 'title': 'Lineup DJ',
         'content': 'Reveal DJ ou mix preview 45s', 'cta': '"Save + lien bio"'},
        {'days': -13, 'phase': 'Early Bird', 'type': 'Story', 'title': 'Duo Mixte',
         'content': '"1H+1F = 22 € · 4 duos seulement"', 'cta': 'DM pour réserver'},
        {'days': -11, 'phase': 'Early Bird', 'type': 'Story', 'title': 'Fermeture EB ⚠️',
         'content': '"Ce soir minuit = fin des 13 €"', 'cta': 'Compte à rebours'},
        {'days': -10, 'phase': 'Pré-vente', 'type': 'Post', 'title': 'Pré-vente ouverte 🔓',
         'content': '"16 € solo · 12 € filles ×4 · fast track · 62 places"', 'cta': '"Commentez 🔥"'},
        {'days': -7, 'phase': 'Pré-vente', 'type': 'Reel', 'title': 'À quoi s\'attendre',
         'content': 'Clips lieu + tables + danse · storytelling 45s', 'cta': '"Partagez aux indécis"'},
        {'days': -5, 'phase': 'Pré-vente', 'type': 'Story', 'title': 'Dernières places PV',
         'content': '"Pré-vente ferme ce soir"', 'cta': 'QR code billetterie'},
        {'days': -4, 'phase': 'Last Minute', 'type': 'Post', 'title': 'FOMO 🔥',
         'content': '"18 € jusqu\'à dimanche · tables sold out · 25 places"', 'cta': '"X places — lien bio"'},
        {'days': -2, 'phase': 'Last Minute', 'type': 'Reel', 'title': 'Countdown 48h',
         'content': 'Montage urgence + musique', 'cta': '"Dernières places"'},
        {'days': -1, 'phase': 'Last Minute', 'type': 'Story', 'title': 'Demain c\'est le soir',
         'content': '"23h → 5h · tenue soignée · dernière chance"', 'cta': 'Géotag La Péniche'},
        {'days': 0, 'phase': 'Jour J', 'type': 'Post', 'title': '🎉 Ce soir !',
         'content': '"Ce soir — 23h — 18 € avant 00h / 22 € après 01h"', 'cta': 'Stories live dès 22h'},
    ]
    
    for data in instagram_data:
        InstagramPost.objects.create(
            event=event,
            scheduled_date=event_date + timedelta(days=data['days']),
            days_before=abs(data['days']),
            phase=data['phase'],
            post_type=data['type'],
            title=data['title'],
            content=data['content'],
            cta=data['cta'],
            status='pending_approval',
        )
    
    # Scénarios de simulation
    scenarios = [
        {'type': 'pessimistic', 'pax': 150, 'bar': 15, 'tpe': 40},
        {'type': 'neutral', 'pax': 200, 'bar': 25, 'tpe': 60},
        {'type': 'optimistic', 'pax': 280, 'bar': 35, 'tpe': 80},
    ]
    
    for s in scenarios:
        SimulationScenario.objects.create(
            event=event,
            scenario_type=s['type'],
            total_pax=s['pax'],
            bar_spend_per_person=s['bar'],
            tpe_percent=s['tpe'],
        )
    
    # Données de ventes simulées
    generate_sample_sales(event)


def generate_sample_sales(event):
    """Génère des données de ventes simulées sur 24 jours."""
    phases = list(event.pricing_phases.all())
    if not phases:
        return
        
    # Distribution des ventes par jour (simulée)
    sales_pattern = {
        # J-24 à J-18 (Super EB) - pic d'ouverture
        -24: {'F': 8, 'M': 3}, -23: {'F': 5, 'M': 2}, -22: {'F': 4, 'M': 2},
        -21: {'F': 3, 'M': 1}, -20: {'F': 4, 'M': 2}, -19: {'F': 6, 'M': 3}, -18: {'F': 5, 'M': 2},
        # J-17 à J-11 (Early Bird)
        -17: {'F': 7, 'M': 4}, -16: {'F': 5, 'M': 3}, -15: {'F': 6, 'M': 4},
        -14: {'F': 4, 'M': 3}, -13: {'F': 5, 'M': 3}, -12: {'F': 6, 'M': 4}, -11: {'F': 8, 'M': 5},
        # J-10 à J-5 (Pré-vente)
        -10: {'F': 6, 'M': 4}, -9: {'F': 4, 'M': 3}, -8: {'F': 5, 'M': 4},
        -7: {'F': 6, 'M': 5}, -6: {'F': 5, 'M': 4}, -5: {'F': 7, 'M': 5},
        # J-4 à J-1 (Last Minute) - pic masculin
        -4: {'F': 4, 'M': 6}, -3: {'F': 3, 'M': 5}, -2: {'F': 4, 'M': 7}, -1: {'F': 5, 'M': 8},
    }
    
    for day_offset, genders in sales_pattern.items():
        sale_date = event.date + timedelta(days=day_offset)
        phase = next((p for p in phases if p.start_date <= sale_date <= p.end_date), None)
        if not phase:
            continue
            
        for gender, count in genders.items():
            if count > 0:
                TicketSale.objects.create(
                    event=event,
                    pricing_phase=phase,
                    sale_date=sale_date,
                    ticket_type='solo',
                    quantity=count,
                    gender=gender,
                    amount=count * float(phase.price_solo),
                )


# ==================== VIEWS ====================

def dashboard(request):
    """Vue d'ensemble / dashboard principal."""
    event = get_or_create_default_event()
    
    # Calculer les métriques clés
    total_sold = sum(
        sale.quantity for sale in event.ticket_sales.all()
    )
    
    # Recettes tables
    tables_booked = event.vip_tables.filter(is_booked=True)
    tables_revenue = sum(t.net_revenue for t in tables_booked)
    tables_pax = sum(t.included_guests for t in tables_booked)
    
    # Dépenses
    fixed_expenses = sum(float(b.amount) for b in event.budget_lines.filter(section='fixed'))
    human_expenses = sum(float(b.amount) for b in event.budget_lines.filter(section='human'))
    
    # Ratio genre
    female_sales = sum(s.quantity for s in event.ticket_sales.filter(gender='F'))
    male_sales = sum(s.quantity for s in event.ticket_sales.filter(gender='M'))
    total_gender = female_sales + male_sales
    female_ratio = (female_sales / total_gender * 100) if total_gender > 0 else 0
    
    # Alertes
    alerts = []
    if not event.venue_approval_received:
        alerts.append({
            'type': 'warning',
            'message': 'Accord INWEE en attente — Publications Instagram verrouillées'
        })
    if female_ratio < 40 and total_gender > 0:
        alerts.append({
            'type': 'danger',
            'message': f'Ratio femmes critique : {female_ratio:.1f}% (objectif ≥ 45%)'
        })
    
    # Jours restants
    days_until = (event.date - date.today()).days
    
    context = {
        'event': event,
        'total_sold': total_sold,
        'tables_revenue': tables_revenue,
        'tables_pax': tables_pax,
        'fixed_expenses': fixed_expenses,
        'human_expenses': human_expenses,
        'female_ratio': female_ratio,
        'male_ratio': 100 - female_ratio if total_gender > 0 else 0,
        'alerts': alerts,
        'days_until': days_until,
        'pricing_phases': event.pricing_phases.all(),
    }
    
    return render(request, 'events/dashboard.html', context)


def event_detail(request, pk):
    """Détail d'un événement."""
    event = get_object_or_404(Event, pk=pk)
    return render(request, 'events/event_detail.html', {'event': event})


def event_create(request):
    """Créer un nouvel événement."""
    if request.method == 'POST':
        event = Event.objects.create(
            name=request.POST.get('name', 'Nouvel événement'),
            venue=request.POST.get('venue', ''),
            date=request.POST.get('date'),
            capacity=int(request.POST.get('capacity', 300)),
        )
        create_default_data(event)
        return redirect('events:dashboard')
    return render(request, 'events/event_create.html')


def simulation(request, pk):
    """Module 1: Simulation financière dynamique."""
    event = get_object_or_404(Event, pk=pk)
    scenarios = event.scenarios.all()
    
    # Calculer les données pour la frise temporelle
    timeline_data = generate_timeline_data(event)
    
    context = {
        'event': event,
        'scenarios': scenarios,
        'timeline_data': json.dumps(timeline_data),
    }
    
    return render(request, 'events/simulation.html', context)


def generate_timeline_data(event):
    """Génère les données pour la frise temporelle à double échelle."""
    data = {
        'pre_event': [],  # J-24 à J-0
        'night': [],      # 23h à 05h
        'expenses': [],   # Marqueurs de dépenses
        'attendance': [], # Courbes filles/garçons dans la salle
    }
    
    # Dépenses pré-événement
    data['expenses'] = [
        {'day': -21, 'label': 'Dépôt La Péniche', 'amount': 3000, 'type': 'expense'},
        {'day': -7, 'label': 'Communication', 'amount': 1000, 'type': 'expense'},
        {'day': -3, 'label': 'Solde La Péniche', 'amount': 1800, 'type': 'expense'},
        {'day': 0, 'label': 'Alcool', 'amount': 2000, 'type': 'expense'},
    ]
    
    # Courbe de trésorerie simulée
    cumulative = 0
    ticket_revenue = 0
    for day in range(-24, 1):
        # Ventes du jour
        day_sales = event.ticket_sales.filter(
            sale_date=event.date + timedelta(days=day)
        ).aggregate(total=models.Sum('amount'))['total'] or 0
        
        ticket_revenue += float(day_sales)
        
        # Dépenses du jour
        day_expense = sum(
            e['amount'] for e in data['expenses'] if e['day'] == day
        )
        
        cumulative += float(day_sales) - day_expense
        
        data['pre_event'].append({
            'day': day,
            'cumulative_revenue': ticket_revenue,
            'treasury': cumulative,
        })
    
    # Simulation de la nuit (23h-05h)
    night_hours = ['23:00', '00:00', '01:00', '02:00', '03:00', '04:00', '05:00']
    attendance_pattern = [0.2, 0.6, 1.0, 0.95, 0.7, 0.4, 0.1]  # % du pic
    
    for i, hour in enumerate(night_hours):
        pax_factor = attendance_pattern[i]
        data['night'].append({
            'hour': hour,
            'girls': int(120 * pax_factor),  # Estimation
            'boys': int(80 * pax_factor),
        })
    
    return data


def pricing(request, pk):
    """Module 2: Calendrier de tarification avec stocks."""
    event = get_object_or_404(Event, pk=pk)
    phases = event.pricing_phases.all()
    
    # Calculer le total des places
    total_places = sum(p.total_places for p in phases)
    sold_places = sum(p.sold_places for p in phases)
    
    context = {
        'event': event,
        'phases': phases,
        'total_places': total_places,
        'sold_places': sold_places,
        'remaining_places': total_places - sold_places,
    }
    
    return render(request, 'events/pricing.html', context)


def tables(request, pk):
    """Module 3: Gestion des tables VIP."""
    event = get_object_or_404(Event, pk=pk)
    tables = event.vip_tables.all()
    
    # Calculs globaux
    booked_tables = tables.filter(is_booked=True)
    total_gross = sum(t.gross_revenue for t in booked_tables)
    total_commission = sum(t.commission_amount for t in booked_tables)
    total_net = sum(t.net_revenue for t in booked_tables)
    total_pax = sum(t.included_guests for t in booked_tables)
    
    context = {
        'event': event,
        'tables': tables,
        'total_gross': total_gross,
        'total_commission': total_commission,
        'total_net': total_net,
        'total_pax': total_pax,
        'formula_choices': VIPTable.FORMULA_CHOICES,
    }
    
    return render(request, 'events/tables.html', context)


def instagram(request, pk):
    """Module 4: Stratégie Instagram & calendrier."""
    event = get_object_or_404(Event, pk=pk)
    posts = event.instagram_posts.all()
    
    # Filtres
    phase_filter = request.GET.get('phase', '')
    type_filter = request.GET.get('type', '')
    
    if phase_filter:
        posts = posts.filter(phase=phase_filter)
    if type_filter:
        posts = posts.filter(post_type=type_filter)
    
    # Phases uniques pour le filtre
    all_phases = event.instagram_posts.values_list('phase', flat=True).distinct()
    
    context = {
        'event': event,
        'posts': posts,
        'all_phases': all_phases,
        'phase_filter': phase_filter,
        'type_filter': type_filter,
        'venue_approval': event.venue_approval_received,
    }
    
    return render(request, 'events/instagram.html', context)


def budget(request, pk):
    """Module 5: Budget consolidé & P&L."""
    event = get_object_or_404(Event, pk=pk)
    
    # Organiser les lignes par section
    revenue_lines = event.budget_lines.filter(section='revenue')
    fixed_lines = event.budget_lines.filter(section='fixed')
    human_lines = event.budget_lines.filter(section='human')
    
    # Calculs
    # Recettes estimées (depuis simulation neutre)
    neutral = event.scenarios.filter(scenario_type='neutral').first()
    
    # Recettes tables
    tables_net = sum(t.net_revenue for t in event.vip_tables.filter(is_booked=True))
    
    # Recettes tickets
    ticket_revenue = sum(float(s.amount) for s in event.ticket_sales.all())
    
    # Totaux
    total_fixed = sum(float(b.amount) for b in fixed_lines)
    total_human = sum(float(b.amount) for b in human_lines)
    
    # Séparer avant/nuit pour la trésorerie
    expenses_avant = sum(float(b.amount) for b in fixed_lines.filter(timing='avant'))
    expenses_nuit = sum(float(b.amount) for b in fixed_lines.filter(timing='nuit'))
    
    total_revenue = ticket_revenue + tables_net
    treasury_end_night = total_revenue - total_fixed
    net_result = treasury_end_night - total_human
    margin = (net_result / total_revenue * 100) if total_revenue > 0 else 0
    
    context = {
        'event': event,
        'revenue_lines': revenue_lines,
        'fixed_lines': fixed_lines,
        'human_lines': human_lines,
        'total_revenue': total_revenue,
        'ticket_revenue': ticket_revenue,
        'tables_net': tables_net,
        'total_fixed': total_fixed,
        'total_human': total_human,
        'expenses_avant': expenses_avant,
        'expenses_nuit': expenses_nuit,
        'treasury_end_night': treasury_end_night,
        'net_result': net_result,
        'margin': margin,
    }
    
    return render(request, 'events/budget.html', context)


def sales(request, pk):
    """Module 6: Suivi des ventes de billets."""
    event = get_object_or_404(Event, pk=pk)
    
    # Agréger les ventes par jour et genre
    sales_data = {}
    for sale in event.ticket_sales.all():
        day_str = sale.sale_date.isoformat()
        if day_str not in sales_data:
            sales_data[day_str] = {'F': 0, 'M': 0}
        sales_data[day_str][sale.gender] += sale.quantity
    
    # Totaux
    total_female = sum(s.quantity for s in event.ticket_sales.filter(gender='F'))
    total_male = sum(s.quantity for s in event.ticket_sales.filter(gender='M'))
    
    context = {
        'event': event,
        'sales_data': json.dumps(sales_data),
        'total_female': total_female,
        'total_male': total_male,
        'total_sold': total_female + total_male,
        'capacity': event.ticketable_capacity,
    }
    
    return render(request, 'events/sales.html', context)


def outils(request, pk):
    """Page Outils avec liens utiles."""
    event = get_object_or_404(Event, pk=pk)
    return render(request, 'events/outils.html', {'event': event})


# ==================== API ENDPOINTS ====================

@require_POST
def api_simulate(request, pk):
    """API pour recalculer la simulation en temps réel."""
    event = get_object_or_404(Event, pk=pk)
    
    try:
        data = json.loads(request.body)
        
        total_pax = int(data.get('total_pax', 200))
        staff_count = int(data.get('staff_count', event.staff_count))
        vip_count = int(data.get('vip_count', event.vip_invited_count))
        vip_cost = float(data.get('vip_cost', event.vip_cost_per_person))
        bar_spend = float(data.get('bar_spend', 25))
        tpe_percent = float(data.get('tpe_percent', 60)) / 100
        
        # Recettes tables
        tables_net = sum(t.net_revenue for t in event.vip_tables.filter(is_booked=True))
        tables_pax = sum(t.included_guests for t in event.vip_tables.filter(is_booked=True))
        
        # Recettes entrées (estimation)
        paying_pax = total_pax - staff_count - tables_pax
        ticket_revenue = paying_pax * 15  # Prix moyen
        
        # Recettes bar
        bar_gross = paying_pax * bar_spend
        bar_tpe_amount = bar_gross * tpe_percent
        bar_commission = bar_tpe_amount * float(event.tpe_commission)
        bar_net = bar_gross - bar_commission
        
        total_revenue = ticket_revenue + tables_net + bar_net
        
        # VIP invités
        vip_total = vip_count * vip_cost
        
        # Dépenses
        fixed_expenses = sum(float(b.amount) for b in event.budget_lines.filter(section='fixed'))
        human_expenses = sum(float(b.amount) for b in event.budget_lines.filter(section='human'))
        
        total_expenses = fixed_expenses + human_expenses
        net_result = total_revenue - total_expenses
        margin = (net_result / total_revenue * 100) if total_revenue > 0 else 0
        
        # Trésorerie fin de soirée
        treasury = total_revenue - fixed_expenses
        
        return JsonResponse({
            'success': True,
            'results': {
                'ticket_revenue': round(ticket_revenue, 2),
                'tables_net': round(tables_net, 2),
                'bar_net': round(bar_net, 2),
                'total_revenue': round(total_revenue, 2),
                'total_expenses': round(total_expenses, 2),
                'treasury': round(treasury, 2),
                'net_result': round(net_result, 2),
                'margin': round(margin, 1),
                'vip_cost': round(vip_total, 2),
            }
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@require_POST
def api_update_table(request, pk):
    """API pour mettre à jour une table VIP."""
    event = get_object_or_404(Event, pk=pk)
    
    try:
        data = json.loads(request.body)
        table_id = data.get('table_id')
        table = get_object_or_404(VIPTable, pk=table_id, event=event)
        
        if 'formula' in data:
            formula = data['formula']
            table.formula = int(formula) if formula else None
            table.is_booked = formula is not None
            # Auto-ajuster commission
            if table.formula:
                table.promo_percent = 15 if table.formula >= 500 else 10
        
        if 'double_order' in data:
            table.double_order = data['double_order']
        
        if 'promo_percent' in data:
            table.promo_percent = float(data['promo_percent'])
        
        if 'promoter_name' in data:
            table.promoter_name = data['promoter_name']
        
        table.save()
        
        # Recalculer les totaux
        booked_tables = event.vip_tables.filter(is_booked=True)
        
        return JsonResponse({
            'success': True,
            'table': {
                'id': table.id,
                'gross_revenue': table.gross_revenue,
                'commission': table.commission_amount,
                'net_revenue': table.net_revenue,
                'guests': table.included_guests,
            },
            'totals': {
                'gross': sum(t.gross_revenue for t in booked_tables),
                'commission': sum(t.commission_amount for t in booked_tables),
                'net': sum(t.net_revenue for t in booked_tables),
                'pax': sum(t.included_guests for t in booked_tables),
            }
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@require_POST
def api_update_budget(request, pk):
    """API pour mettre à jour une ligne de budget."""
    event = get_object_or_404(Event, pk=pk)
    
    try:
        data = json.loads(request.body)
        
        if 'line_id' in data:
            # Mise à jour d'une ligne existante
            line = get_object_or_404(BudgetLine, pk=data['line_id'], event=event)
            
            if 'name' in data:
                line.name = data['name']
            if 'amount' in data:
                line.amount = Decimal(str(data['amount']))
            if 'timing' in data:
                line.timing = data['timing']
            
            line.save()
        
        elif 'action' in data and data['action'] == 'add':
            # Nouvelle ligne
            BudgetLine.objects.create(
                event=event,
                name=data.get('name', 'Nouvelle dépense'),
                amount=Decimal(str(data.get('amount', 0))),
                timing=data.get('timing', 'avant'),
                section=data.get('section', 'fixed'),
            )
        
        # Recalculer les totaux
        fixed_lines = event.budget_lines.filter(section='fixed')
        human_lines = event.budget_lines.filter(section='human')
        
        return JsonResponse({
            'success': True,
            'totals': {
                'fixed': float(sum(b.amount for b in fixed_lines)),
                'human': float(sum(b.amount for b in human_lines)),
            }
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@require_POST
def api_update_instagram(request, pk):
    """API pour mettre à jour le statut d'une publication Instagram."""
    event = get_object_or_404(Event, pk=pk)
    
    try:
        data = json.loads(request.body)
        post_id = data.get('post_id')
        post = get_object_or_404(InstagramPost, pk=post_id, event=event)
        
        if 'status' in data:
            post.status = data['status']
            post.save()
        
        return JsonResponse({
            'success': True,
            'post': {
                'id': post.id,
                'status': post.status,
                'is_locked': post.is_locked,
            }
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@require_GET
def api_sales_data(request, pk):
    """API pour récupérer les données de ventes."""
    event = get_object_or_404(Event, pk=pk)
    
    # Agréger par jour
    daily_data = {}
    cumulative_f = 0
    cumulative_m = 0
    
    for day in range(-24, 1):
        sale_date = event.date + timedelta(days=day)
        day_str = sale_date.isoformat()
        
        f_sales = event.ticket_sales.filter(
            sale_date=sale_date, gender='F'
        ).aggregate(total=models.Sum('quantity'))['total'] or 0
        
        m_sales = event.ticket_sales.filter(
            sale_date=sale_date, gender='M'
        ).aggregate(total=models.Sum('quantity'))['total'] or 0
        
        cumulative_f += f_sales
        cumulative_m += m_sales
        
        daily_data[day_str] = {
            'day': day,
            'daily_f': f_sales,
            'daily_m': m_sales,
            'cumulative_f': cumulative_f,
            'cumulative_m': cumulative_m,
            'cumulative_total': cumulative_f + cumulative_m,
        }
    
    # Phases pour les marqueurs
    phases = [
        {'name': p.name, 'start': p.start_date.isoformat(), 'end': p.end_date.isoformat()}
        for p in event.pricing_phases.all()
    ]
    
    return JsonResponse({
        'success': True,
        'daily': daily_data,
        'phases': phases,
        'capacity': event.ticketable_capacity,
    })


# Import manquant pour les agrégations
from django.db import models
