from django.shortcuts import render, redirect
import requests
import datetime
import json
from hashlib import sha256
from django.http import JsonResponse

from .models import Candidate, RegisteredVoters
from .blockchain import Blockchain
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
# from .forms import VoterCreationForm


blockchain = Blockchain()

blockchain.create_genesis_block()

URL = "http://127.0.0.1:8000"

#########################################################################################

def register_page(request):
	if request.method == 'POST':
	# Get form values
		username = request.POST.get('username')
		name = request.POST.get('name')
		email = request.POST.get('email')
		phone = request.POST.get('phone')
		age = request.POST.get('age')
		password = request.POST.get('password')
		password2 = request.POST.get('password2')

		# Check if passwords match
		if password == password2:
			# Check username
			if RegisteredVoters.objects.filter(username=username).exists():
				messages.error(request, 'That username is taken')
				return redirect('register')
			else:
				if RegisteredVoters.objects.filter(email=email).exists():
					messages.error(request, 'That email is being used')
					return redirect('register')
				else:
					user = RegisteredVoters.objects.create_user(username=username, name=name, email=email, phone=phone, age=age, password=password)
					user.save()
					messages.success(request, 'You are now registered and can log in')
					return redirect('login')
		else:
			messages.error(request, 'Passwords do not match')
			return redirect('register')
	else:
		return render(request, 'register.html')


def login_page(request):
	if request.method == 'POST':
		username = request.POST.get('username')
		password = request.POST.get('password')

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

######################################################################################### 

@login_required(login_url='login')
def home(request):
	return render(request, 'landing.html')


@login_required(login_url='login')
def success(request):
	return render(request, 'success.html')


@login_required(login_url='login')
def mine_success(request):
	return render(request, 'mine_success.html')


@login_required(login_url='login')
def mine(request):
	requests.get(f"{URL}/mine_block/")
	return redirect('mine_success')


@login_required(login_url='login')
def voting(request):
	candidate = Candidate.objects.all()
	return render(request, 'voting.html', {'candidates': candidate})


@login_required(login_url='login')
def submit(request):

	if request.method == 'POST':
		data = request.POST

		bools = True

		if bools:
			hash_string = request.POST.get('first_name') + request.POST.get('last_name') + request.POST.get('password') + request.POST.get('unique_id')
			hashed_value = sha256(hash_string.encode()).hexdigest()

			post_object = {
				'candidate': request.POST.get('candidate'),
				'voterhash': hashed_value
			}

			requests.post(f"{URL}/new_transaction/", json=post_object, headers={'Content-type': 'application/json; charset=utf-8'})

			return render(request, 'success.html', {'voter_details': data})
		else:
			return render(request, 'error.html', {'message': "NOT VALID"})


# all votes page





############################################################################################

@csrf_exempt
def new_transaction(request):
	if request.method == 'POST':
		transaction_data = json.loads(request.body)
		print(transaction_data)
		required_fields = ["candidate", "voterhash"]

		for field in required_fields:
			if not transaction_data.get(field):
				return JsonResponse("Invalid transaction data", safe=False, status=404) 

		if (transaction_data["voterhash"] in blockchain.voted):
			return JsonResponse('Cannot vote more than once')

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