from django.shortcuts import render,redirect
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.views import View
from django.http import HttpResponse
from django.views.generic import CreateView, ListView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from transactions.constants import DEPOSIT, WITHDRAWAL
from datetime import datetime
from django.db.models import Sum
from transactions.forms import (DepositForm,WithdrawForm)
from transactions.models import Transaction
from accounts.models import UserAccount
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template.loader import render_to_string


class TransactionCreateMixin(LoginRequiredMixin, CreateView):
    template_name = 'transactions/transaction_form.html'
    model = Transaction
    title = ''
    success_url = reverse_lazy('homepage')  # Set homepage as the success URL

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'account': self.request.user.account
        })
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) 
        context.update({
            'title': self.title
        })
        return context

def send_transaction_email(user, amount, subject, template):
    message = render_to_string(template, {
        'user' : user,
        'amount' : amount,
    })
    send_email = EmailMultiAlternatives(subject, '', to=[user.email])
    send_email.attach_alternative(message, "text/html")
    send_email.send()


class DepositMoneyView(TransactionCreateMixin):
    form_class = DepositForm
    title = 'Deposit'

    def get_initial(self):
        initial = {'transaction_type': DEPOSIT}
        return initial

    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')
        account = self.request.user.account
        account.balance += amount
        account.save(update_fields=['balance'])

        messages.success(self.request, f'{"{:,.2f}".format(float(amount))}$ was deposited to your account successfully')
        # send_transaction_email(self.request.user, amount, "Deposite Message", "transactions/deposite_email.html")
        return super().form_valid(form)


class WithdrawMoneyView(TransactionCreateMixin):
    form_class = WithdrawForm
    title = 'Withdraw Money'

    def get_initial(self):
        initial = {'transaction_type': WITHDRAWAL}
        return initial

    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')

        self.request.user.account.balance -= form.cleaned_data.get('amount')
        self.request.user.account.save(update_fields=['balance'])

        messages.success(self.request,f'Successfully, Pet Adoption amount {"{:,.2f}".format(float(amount))}$ has been deducted from your account')
        return super().form_valid(form)