from django.shortcuts import get_object_or_404, render, redirect

from .models import Question
from django.views.generic.edit import FormView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login
from django.http import HttpResponseRedirect
from django.views.generic.base import View
from django.contrib.auth import logout
from django.contrib.auth.forms import PasswordChangeForm
from .models import Answer
from datetime import datetime
from django.http import JsonResponse
import json



def index(request):
    message = None
    if "message" in request.GET:
        message = request.GET["message"]
    return render(
        request,
        "index.html",
        {
            "latest_questions":
                Question.objects.order_by('-rating'),
            "message": message
        }
    )

app_url = "/questions/"

class RegisterFormView(FormView):
    # будем строить на основе
    # встроенной в django формы регистрации
    form_class = UserCreationForm
    # Ссылка, на которую будет перенаправляться пользователь
    # в случае успешной регистрации.
    # В данном случае указана ссылка на
    # страницу входа для зарегистрированных пользователей.
    success_url = app_url + "login/"
    # Шаблон, который будет использоваться
    # при отображении представления.
    template_name = "reg/register.html"
    def form_valid(self, form):
        # Создаём пользователя,
        # если данные в форму были введены корректно.
        form.save()
        # Вызываем метод базового класса
        return super(RegisterFormView, self).form_valid(form)

class LoginFormView(FormView):

    form_class = AuthenticationForm
    template_name = "reg/login.html"
    success_url = app_url
    def form_valid(self, form):
        self.user = form.get_user()
        login(self.request, self.user)
        return super(LoginFormView, self).form_valid(form)

class LogoutView(View):
    def get(self, request):
        # Выполняем выход для пользователя,
        # запросившего данное представление.
        logout(request)
        # После чего перенаправляем пользователя на
        # главную страницу.
        return HttpResponseRedirect(app_url)

class PasswordChangeView(FormView):
    # будем строить на основе
    # встроенной в django формы смены пароля
    form_class = PasswordChangeForm
    template_name = 'reg/password_change_form.html'
    # после смены пароля нужно снова входить
    success_url = app_url + 'login/'
    def get_form_kwargs(self):
        kwargs = super(PasswordChangeView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        if self.request.method == 'POST':
            kwargs['data'] = self.request.POST
        return kwargs
    def form_valid(self, form):
        form.save()
        return super(PasswordChangeView, self).form_valid(form)

def detail(request, question_id):
    error_message = None
    if "error_message" in request.GET:
        error_message = request.GET["error_message"]
    return render(
        request,
        "answers.html",
        dict(question=get_object_or_404(Question, pk=question_id), error_message=error_message,
             latest_answers=Answer.objects
             .filter(chat_id=question_id)
             .order_by('-pub_date'))
    )

def post(request, question_id):
    ans = Answer()
    ans.author = request.user
    ans.chat = get_object_or_404(Question, pk=question_id)
    ans.message = request.POST['message']
    ans.pub_date = datetime.now()
    ans.save()
    return HttpResponseRedirect(app_url+str(question_id))

def rate_question(request, question_id):
    quest = get_object_or_404(Question, pk=question_id)
    quest.rating += 1
    quest.save()
    return HttpResponseRedirect(app_url+str(question_id))

def rate_answer(request, answer_id):
    ans = get_object_or_404(Answer, pk=answer_id)
    ans.rating += 1
    ans.save()
    return HttpResponseRedirect(app_url + str(ans.chat_id))

def msg_list(request, question_id):
    res = list(
            Answer.objects
                .filter(chat_id=question_id)
                .order_by('-rating')
                .values('author__username',
                        'pub_date',
                        'message', 'rating'
                )
            )
    for r in res:
        r['pub_date'] = \
            r['pub_date'].strftime(
                '%d.%m.%Y %H:%M:%S'
            )
    return JsonResponse(json.dumps(res), safe=False)

