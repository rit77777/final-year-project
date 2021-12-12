from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout

import json
import requests
import datetime
from hashlib import sha256

from .models import Candidate, RegisteredVoters, UniqueID
from .blockchain import Blockchain


# ------------Initializing blockchain-----------------------

blockchain = Blockchain()

blockchain.create_genesis_block()

candidates = Candidate.objects.all()
candidates = list(candidates)
blockchain.create_candidates(candidates)

URL = "http://127.0.0.1:8000"


# ------------Registration And Login-----------------------

def register_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        age = request.POST.get('age')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        try:
            unique_id_details = UniqueID.objects.get(unique_id=username)
        except:
            messages.error(request, 'Unique id doesnot exists')
            return redirect('register')

        if username != unique_id_details.unique_id:
            messages.error(request, 'Unique id is invalid')
            return redirect('register')

        if email != unique_id_details.email:
            messages.error(request, 'email does not match unique id email')
            return redirect('register')

        if phone != unique_id_details.phone:
            messages.error(request, 'phone no does not match unique id email')
            return redirect('register')

        if int(age) < 18 or int(unique_id_details.age) < 18:
            messages.error(request, 'You must be 18+ to vote')
            return redirect('register')

        if int(age) != int(unique_id_details.age):
            messages.error(request, 'Age does not match with unique_id age')
            return redirect('register')

        if password != password2:
            messages.error(request, 'Passwords do not match')
            return redirect('register')

        if RegisteredVoters.objects.filter(username=username).exists():
            messages.error(request, 'That username is taken')
            return redirect('register')

        if RegisteredVoters.objects.filter(email=email).exists():
            messages.error(request, 'That email is already registered')
            return redirect('register')

        if RegisteredVoters.objects.filter(phone=phone).exists():
            messages.error(request, 'That phone no is already registered')
            return redirect('register')

        try:
            user = RegisteredVoters.objects.create_user(username=username, name=name, email=email, phone=phone, age=age, password=password)
            user.save()
            messages.success(request, 'You are now registered and can log in')
            return redirect('login')
        except:
            messages.error(request, 'error while registering')
            return redirect('register')
    else:
        return render(request, 'register.html')


def login_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        voter = RegisteredVoters.objects.get(username=username)
        if voter.vote_done:
            messages.error(request, 'You have already voted')
            return redirect('login')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, 'You are now logged in')
            return redirect('home')
        else:
            messages.error(request, 'Invalid credentials')
            return redirect('login')
    else:
        return render(request, 'login.html')


def logout_page(request):
    logout(request)
    messages.success(request, 'You are now logged out')
    return redirect('home')


# ------------Voting Phase-----------------------

def home(request):
    return render(request, 'landing.html')


@login_required(login_url='login')
def voting(request):
    if request.user.vote_done:
        messages.error(request, 'You cannot vote more than once')
        return redirect('home')
    else:
        candidates = Candidate.objects.all()
        return render(request, 'voting.html', {'candidates': candidates})


@login_required(login_url='login')
def submit(request):
    if request.method == 'POST':
        data = request.POST

        if request.user.is_authenticated:
            voter = RegisteredVoters.objects.get(username=request.user.username)
            voter_hash_string = str(request.user.username) + str(request.user.email) + str(request.user.name) + str(request.user.phone) + str(request.user.age)
            voter_hashed_value = sha256(voter_hash_string.encode()).hexdigest()

            vote_transaction = {
                'candidate': request.POST.get('candidate'),
                'voterhash': voter_hashed_value
            }

            response = requests.post(f"{URL}/new_transaction/", json=vote_transaction, headers={'Content-type': 'application/json'})

            response_data = response.json()
            print(response_data)

            if response.status_code == 201:
                voter.vote_done = True
                voter.save()
                return render(request, 'success.html', {'voter_details': data})
            else:
                return render(request, 'error.html', {'error_message': response_data['error']})
        else:
            return render(request, 'error.html', {'error_message': "NOT VALID"})


@login_required(login_url='login')
def success(request):
    return render(request, 'success.html')


@login_required(login_url='login')
def mine(request):
    requests.get(f"{URL}/mine_block/")
    return redirect('mine_success')


@login_required(login_url='login')
def mine_success(request):
    return render(request, 'mine_success.html')


# ------------Result-----------------------

def all_votes(request):
    vote_data = []
    response = requests.get(f"{URL}/get_chain")
    if response.status_code == 200:
        chain_data = json.loads(response.content)
        for block in chain_data["chain"]:
            for transaction in block["transactions"]:
                transaction["index"] = block["index"]
                vote_data.append(transaction)

        print("final", vote_data)
    
    return render(request, 'all_votes.html', {'vote_details': vote_data})


def count_votes(request):
    data = blockchain.get_result()
    print(data)
    return render(request, 'count_votes.html', {'vote_count': data})


def chart_votes(request):
    data = blockchain.get_result()
    print(data)
    keys_data = list(data.keys())
    print("chart", keys_data)
    values_data = list(data.values())
    print("chart", values_data)
    return render(request, 'count_votes_graph.html', {'count': values_data, 'names': keys_data})


# ------------Blockchain calls-----------------------

@csrf_exempt
def new_transaction(request):
    if request.method == 'POST':
        transaction_data = json.loads(request.body)
        print(transaction_data)
        required_fields = ["candidate", "voterhash"]

        for field in required_fields:
            if not transaction_data.get(field):
                return JsonResponse({'error': 'Invalid transaction data'}, safe=False, status=404) 

        if (transaction_data["voterhash"] in blockchain.voted):
            return JsonResponse({'error': 'You cannot vote more than once'}, status=400)

        transaction_data["timestamp"] = str(datetime.datetime.now())

        blockchain.add_new_transaction(transaction_data)

        return JsonResponse("Success", safe=False, status=201)


def get_chain(request):
    chain_data = []
    for block in blockchain.chain:
        chain_data.append(block.__dict__)

    data = {
        "length": len(chain_data),
        "chain": chain_data
    }
    return JsonResponse(data, safe=False, status=200)


def mine_block(request):
    result = blockchain.mine()
    if not result:
        return JsonResponse("No transactions in queue to mine", safe=False, status=404)
    else:
        return JsonResponse(f"Block #{blockchain.last_block.index} is mined. Your vote is now added to the blockchain", safe=False, status=201)


def pending_transaction(request):
    return JsonResponse({'pending': blockchain.unconfirmed_transactions }, status=200)