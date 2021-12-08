from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('success/', views.success, name='success'),
    path('mine_success/', views.mine_success, name='mine_success'),
    path('mine/', views.mine, name='mine'),
    path('voting/', views.voting, name='voting'),
    # path('all_votes/', views.all_votes, name='all_votes'),
    path('submit/', views.submit, name='submit'),
    # path('count_votes/', views.count_votes, name='count_votes'),

    ########################################################
    path('new_transaction/', views.new_transaction, name='new_transaction'),
    path('get_chain/', views.get_chain, name='get_chain'),
    path('mine_block/', views.mine_block, name='mine_block'),
    path('pending_transaction/', views.pending_transaction, name='pending_transaction'),
]