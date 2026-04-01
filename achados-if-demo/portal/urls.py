from django.urls import path

from . import views

app_name = "portal"
urlpatterns = [
    path("", views.index, name="index"),
    path("mural/", views.board, name="board"),
    path("itens/publicar/", views.publish_item, name="publish_item"),
    path("auth/teste/", views.demo_login, name="demo_login"),
    path("auth/sair/", views.sign_out, name="sign_out"),
    path("conta/", views.account, name="account"),
    path("gestao/", views.management, name="management"),
    path("gestao/itens/<int:pk>/editar/", views.edit_item, name="edit_item"),
    path("gestao/itens/<int:pk>/status/", views.toggle_resolution, name="toggle_resolution"),
    path("gestao/itens/<int:pk>/excluir/", views.delete_item, name="delete_item"),
]
