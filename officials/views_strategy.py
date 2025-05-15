from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from .models import Strategy
from .forms_strategy import StrategyForm


@login_required
def strategy_list(request):
    """Display list of officiating strategies."""
    strategies = Strategy.objects.all().order_by('name')
    paginator = Paginator(strategies, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'officials/strategy_list.html', {
        'page_obj': page_obj,
    })


@login_required
def strategy_detail(request, pk):
    """Display details of a specific strategy."""
    strategy = get_object_or_404(Strategy, pk=pk)
    
    return render(request, 'officials/strategy_detail.html', {
        'strategy': strategy,
    })


@login_required
def strategy_create(request):
    """Create a new strategy."""
    if not request.user.is_staff:
        messages.error(request, 'Only staff members can create strategies.')
        return redirect('strategy_list')
    
    if request.method == 'POST':
        form = StrategyForm(request.POST)
        if form.is_valid():
            strategy = form.save()
            messages.success(request, f'Strategy {strategy.get_name_display()} created successfully!')
            return redirect('strategy_detail', pk=strategy.pk)
    else:
        form = StrategyForm()
    
    return render(request, 'officials/strategy_form.html', {
        'form': form,
        'title': 'Create Strategy',
    })


@login_required
def strategy_update(request, pk):
    """Update an existing strategy."""
    strategy = get_object_or_404(Strategy, pk=pk)
    
    # Check if user has permission to edit this strategy
    if not request.user.is_staff:
        messages.error(request, 'Only staff members can edit strategies.')
        return redirect('strategy_list')
    
    if request.method == 'POST':
        form = StrategyForm(request.POST, instance=strategy)
        if form.is_valid():
            form.save()
            messages.success(request, f'Strategy {strategy.get_name_display()} updated successfully!')
            return redirect('strategy_detail', pk=strategy.pk)
    else:
        form = StrategyForm(instance=strategy)
    
    return render(request, 'officials/strategy_form.html', {
        'form': form,
        'title': 'Update Strategy',
        'strategy': strategy,
    })


@login_required
def strategy_delete(request, pk):
    """Delete an existing strategy."""
    strategy = get_object_or_404(Strategy, pk=pk)
    
    # Check if user has permission to delete this strategy
    if not request.user.is_staff:
        messages.error(request, 'Only staff members can delete strategies.')
        return redirect('strategy_list')
    
    if request.method == 'POST':
        strategy_name = strategy.get_name_display()
        strategy.delete()
        messages.success(request, f'Strategy {strategy_name} deleted successfully!')
        return redirect('strategy_list')
    
    return render(request, 'officials/strategy_confirm_delete.html', {
        'strategy': strategy,
    })
