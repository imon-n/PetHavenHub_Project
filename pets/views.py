from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView,DeleteView,DetailView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from . import forms

from .models import Pet_Model, PurchaseHistory
from transactions.models import Transaction
from transactions.constants import WITHDRAWAL


@method_decorator(login_required, name='dispatch')
class add_post_CreateView(CreateView):
    model = Pet_Model
    template_name = 'add_post.html'
    form_class = forms.PostForm
    success_url = reverse_lazy("homepage")
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

@method_decorator(login_required, name='dispatch')
class EditPostView(UpdateView):
    model = Pet_Model
    form_class = forms.PostForm
    pk_url_kwarg = 'post_id'
    template_name = 'add_post.html'
    success_url = reverse_lazy("homepage")

@method_decorator(login_required, name='dispatch')
class DeletePostView(DeleteView):
    model = Pet_Model
    template_name = 'delete.html'
    success_url = reverse_lazy("homepage")
    pk_url_kwarg = 'post_id'


@login_required
def profile_history(request):
    purchases = PurchaseHistory.objects.filter(user=request.user)
    return render(request, 'profile_history.html', {'purchases': purchases})

@login_required
def adopt_pet(request, id):
    pet = get_object_or_404(Pet_Model, id=id)
    user_account = request.user.account

    if pet.quantity > 0:
        amount = pet.price
        
        if user_account.balance >= amount:
            user_account.balance -= amount
            user_account.save(update_fields=['balance'])
            
            pet.reduce_quantity()
            
            PurchaseHistory.objects.create(
                user=request.user,
                pet=pet.name,
                category_name=pet.category_name.category_name,
                price=pet.price
            )
            
            Transaction.objects.create(
                account=user_account,
                amount=amount,
                balance_after_transaction=user_account.balance,
                transaction_type=WITHDRAWAL
            )
            if pet.quantity == 0:
                pet.delete()
            
            messages.success(request, f"You have successfully get adoption permision the '{pet.name}'.")
        else:
            messages.error(request, "Insufficient balance to adoption this pet.")
    else:
        messages.error(request, "This pet is out of stock.")

    return redirect('profile_history')
