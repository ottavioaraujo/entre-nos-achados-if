from django.urls import path

from . import views

app_name = "portal"
urlpatterns = [
    path("robots.txt", views.robots_txt, name="robots_txt"),
    path("sitemap.xml", views.sitemap_xml, name="sitemap_xml"),
    path("llms.txt", views.llms_txt, name="llms_txt"),
    path("", views.index, name="index"),
    path("mural/", views.board, name="board"),
    path("itens/publicar/", views.publish_item, name="publish_item"),
    path("itens/<int:pk>/foto/", views.item_photo, name="item_photo"),
    path("itens/<int:pk>/comentarios/", views.publish_comment, name="publish_comment"),
    path("auth/suap/login/", views.suap_login, name="suap_login"),
    path("auth/suap/callback/", views.suap_callback, name="suap_callback"),
    path("auth/sair/", views.sign_out, name="sign_out"),
    path("conta/", views.account, name="account"),
    path("gestao/", views.management, name="management"),
    path("gestao/itens/<int:pk>/editar/", views.edit_item, name="edit_item"),
    path("gestao/itens/<int:pk>/status/", views.toggle_resolution, name="toggle_resolution"),
    path("gestao/itens/<int:pk>/excluir/", views.delete_item, name="delete_item"),
]
