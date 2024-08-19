from django.shortcuts import render,redirect
from .models import *
from .forms import CreateUserForm, ElectionForm, ContestantForm, PositionForm, inlineformset_factory#, ElectionPositionFormset
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.forms import formset_factory
from django.shortcuts import render, get_object_or_404


# Signup, Signin, Signout
#################################################################
def signup(request):
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            
            # Making sure that when a new user register that they become a student
            Student.objects.create(
                user = user,
                name = user.username,
            )

            # automatically logging user in after registration starts here
            username = request.POST['username']
            password = request.POST['password1']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                group = Group.objects.get(name="student")
                user.groups.add(group)
                return redirect("index")
            
    context = {'form': form}
    return render(request, 'signup.html', context)

def signin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request,user)
            return redirect('index')
            messages.info(request,"You are now logged in")
        else:
            messages.info(request, "Username OR password is incorrect")
    return render(request, 'signin.html')

def signout(request):
    logout(request)
    return redirect('signin')
#################################################################

@login_required(login_url='signin')
def index(request):
    # Get all elections
    all_elections = Election.objects.all()
    # Filter out active elections
    elections = [election for election in all_elections if election.is_active]
    # Getting total sum of active elections
    total_ongoing = len(elections)
    role = request.user.groups.all()[0].name
    print(f'Role: {role}')

    # Filter out elections that the current user has already voted for
    if request.user.is_authenticated:
        # Get the current user as a Student
        student = Student.objects.get(user=request.user)
        # Exclude elections that the student has already voted for
        elections = [election for election in elections if election not in student.voted_elections.all()]

    # Getting total elections the user has voted for
    total_voted = student.voted_elections.count()
    # Getting the users past elections the user has voted for
    voted_elections = student.voted_elections.all()
    print(f'VOTED ELECTIONSS: {voted_elections}')
    # # Create a string of all election names
    # past_elections = ', '.join([past_election.name for past_election in past_elections])
    # print(f'PAST ELECTIONS: {past_elections}')

    context = {
        'elections': elections,
        'total_ongoing': total_ongoing,
        'total_voted': total_voted,
        'voted_elections': voted_elections,
        'role': role,
    }
    return render(request, 'index.html', context)

@login_required(login_url='signin')
def viewElection(request, pk):
    role = request.user.groups.all()[0].name
    election = Election.objects.get(id=pk)
    print(f'Election: {election}')
    contestants = election.contestant_set.all()
    print(f'Contestants: {contestants}')
    
    positions = Position.objects.filter(contestant__election=election).distinct()
    print(f'POSITIONS: {positions}')
    selected_candidates = request.POST.getlist('selected_candidates')
    selected_contestants = Contestant.objects.filter(id__in=selected_candidates)

    if selected_candidates != []:
        if request.method == 'POST':
            # Create a dictionary to store positions and corresponding contestants
            positions_and_contestants = {}

            # Loop through each selected contestant and print their information
            for contestant in selected_contestants:
                print(f"Position: {contestant.position}, Contestant: {contestant.student}")
                position = contestant.position
                if position not in positions_and_contestants:
                    positions_and_contestants[position] = []
                positions_and_contestants[position].append(contestant)
            return render(request, 'voted.html', {'positions_and_contestants': positions_and_contestants, 'election': election})
    else:
        messages.error(request, 'You have not selected an Candidate!')
        context = {
            'election' : election,
            'positions':positions,
            'role': role,
        }
        return render(request, 'viewElection.html', context)
    
def submitVote(request):
    if request.method == 'POST':
        # Get the contestant values from the form data
        contestants = request.POST.getlist('contestants[]')
        positions = request.POST.getlist('positions[]')

        voteDict = dict(zip(contestants, positions))
        election_name = request.POST.get('submit-vote')

        # Get the Election object
        election = Election.objects.get(name=election_name)

        print(f'VOTEDICT: {voteDict.items()}')

        # Check if the current user is authenticated
        if request.user.is_authenticated:
            # Get the current user as a Student
            student = Student.objects.get(user=request.user)
            print(f'Students: {student}')

            for elect_name, position_name in voteDict.items():
                print(f'ELECTT: {elect_name.split()[0]}, ELECT NAME: {elect_name}, POSITION NAME: {position_name}')
                contestant = Contestant.objects.get(student__name=elect_name.split()[0], position__name=position_name)
                contestant.total_vote += 1
                contestant.save()

            # Add the election to the student's voted_elections
            student.voted_elections.add(election)
            # Returning success message
            messages.success(request, 'Your vote has been recorded!')
            return redirect('index')
        else:
            messages.error(request, 'You need to be logged in to vote!')
            return redirect('signin')

    # Handle GET requests or other cases
    return render(request, 'viewElection.html')

def viewVotes(request, pk):
    election = get_object_or_404(Election, id=pk)
    positions = election.position_set.all()
    contestants = election.contestant_set.all()

    # Dictionary to hold total votes for each position
    position_totals = {position.id: 0 for position in positions}

    # Calculate the total votes per position
    for contestant in contestants:
        if contestant.position.id in position_totals:
            position_totals[contestant.position.id] += contestant.total_vote

    # Add percentage to each contestant
    for contestant in contestants:
        total_votes = position_totals.get(contestant.position.id, 0)
        if total_votes > 0:
            contestant.vote_percentage = (contestant.total_vote / total_votes) * 100
        else:
            contestant.vote_percentage = 0

    context = {'election': election, 'contestants': contestants}
    return render(request, 'viewVotes.html', context)

@login_required(login_url='signin')
def create_election(request):
    if request.user.groups.filter(name='admin').exists():
        if request.method == 'POST':
            election_form = ElectionForm(request.POST)
            if election_form.is_valid():
                # Save the election first
                election = election_form.save()
                
                # Now handle the dynamic positions
                positions = request.POST.getlist('positions')  # Assuming 'positions' is the name of your dynamic form field
                
                for position_name in positions:
                    position = Position(name=position_name, election=election)
                    position.save()

                messages.success(request, 'Election created successfully.')
                return redirect('viewElection', pk=election.pk)
        else:
            election_form = ElectionForm()

        context = {
            'election_form': election_form,
        }
        return render(request, 'create_election.html', context)
    else:
        messages.error(request, 'You do not have permission to create elections.')
        return redirect('index')
    
# @login_required(login_url='signin')
# def add_contestant(request, pk):
#     if request.user.groups.filter(name='admin').exists():
#         election = get_object_or_404(Election, pk=pk)
        
#         # Define the formset based on ContestantForm
#         ContestantFormSet = formset_factory(ContestantForm, extra=1)
        
#         if request.method == 'POST':
#             formset = ContestantFormSet(request.POST)
#             if formset.is_valid():
#                 for form in formset:
#                     contestant = form.save(commit=False)
#                     contestant.election = election
#                     contestant.save()
#                 messages.success(request, 'Contestants added successfully.')
#                 return redirect('viewElection', pk=election.pk)
#         else:
#             formset = ContestantFormSet()
        
#         context = {
#             'formset': formset,
#             'election': election,
#         }
#         return render(request, 'add_contestant.html', context)
#     else:
#         messages.error(request, 'You do not have permission to add contestants.')
#         return redirect('index')  # Redirect to index or any appropriate page

# @login_required(login_url='signin')
# def add_contestant(request, pk):
#     if request.user.groups.filter(name='admin').exists():
#         election = get_object_or_404(Election, pk=pk)
        
#         if request.method == 'POST':
#             form = ContestantForm(request.POST)
#             if form.is_valid():
#                 contestant = form.save(commit=False)
#                 contestant.election = election
#                 contestant.save()
#                 messages.success(request, 'Contestant added successfully.')
#                 return redirect('viewElection', pk=election.pk)
#         else:
#             form = ContestantForm(initial={'election': election})
        
#         context = {
#             'form': form,
#             'election': election,
#         }
#         return render(request, 'add_contestant.html', context)
#     else:
#         messages.error(request, 'You do not have permission to add contestants.')
#         return redirect('index')  # Redirect to index or any appropriate page

@login_required(login_url='signin')
def add_contestant(request, pk):
    if request.user.groups.filter(name='admin').exists():
        election = get_object_or_404(Election, pk=pk)
        
        if request.method == 'POST':
            form = ContestantForm(request.POST)
            if form.is_valid():
                contestant = form.save(commit=False)
                contestant.election = election
                contestant.save()
                messages.success(request, 'Contestant added successfully.')
                return redirect('viewElection', pk=election.pk)
        else:
            # Initialize form with election and filtered positions queryset
            form = ContestantForm(initial={'election': election})
            form.fields['position'].queryset = Position.objects.filter(election=election)
        
        context = {
            'form': form,
            'election': election,
        }
        return render(request, 'add_contestant.html', context)
    else:
        messages.error(request, 'You do not have permission to add contestants.')
        return redirect('index')  # Redirect to index or any appropriate page
    
# @login_required(login_url='signin')
# def delete_election(request, pk):
#     election = Election.objects.get(id=pk)
#     if request.method == 'POST':
#         election.delete()


@login_required(login_url='signin')
def delete_election(request, pk):
    if request.user.groups.filter(name='admin').exists():
        election = get_object_or_404(Election, pk=pk)
        if request.method == 'POST':
            election.delete()
            messages.success(request, 'Election deleted successfully.')
            return redirect('index')  # Redirect to a relevant page after deletion
        context = {'election': election}
        return render(request, 'delete_election.html', context)
    else:
        messages.error(request, 'You do not have permission to delete elections.')
        return redirect('index')  # Redirect to index or any appropriate page