from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from soundmap.models import Song, UserProfile, User, Playlist
from soundmap.forms import UserForm, UserProfileForm, SongForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import simplejson, json


def index(request):
	context = RequestContext(request)

	song_list = Song.objects.all()
	form=SongForm()
	
	context_dict = {'song_list':song_list, 'form':form}

	return render_to_response('soundmap/index.html', context_dict, context)

@login_required
def add_song(request):
	context = RequestContext(request)
	context_dict={}
	uploader = User.objects.get(username=request.user)

	if request.method=='POST':
		form = SongForm(request.POST)

		if form.is_valid():
			song = form.save(commit=False)
			try:
				uploader_profile = UserProfile.objects.get(user=uploader)
				song.uploader = uploader_profile
			except UserProfile.DoesNotExist:
				uploader_profile=None
			location = request.POST.get('city', None)
			if location:
				song.city = location
				if Playlist.objects.filter(city=location): #Playlist already exists. Append it to that playlist
					song.playlist=Playlist.objects.get(city=location)
				else:
					playlist = Playlist.objects.get_or_create(latitude=request.POST.get('latitude', 0), longitude=request.POST.get('longitude',0), city=location)
					song.playlist=playlist[0]
			else:
				print("error")
			song.listens=0
			song.likes=0
			song.save()

			return HttpResponseRedirect('/soundmap/')	#After submitting the form, redirects the user back to the homepage
		else:
			print form.errors
	else:
		form = SongForm()

	context_dict['form'] = form
	return render_to_response('soundmap/add_song.html', context_dict, context)

def register(request):
    context = RequestContext(request)

    # A boolean value for telling the template whether the registration was successful.
    # Set to False initially. Code changes value to True when registration succeeds.
    registered = False

    # If it's a HTTP POST, we're interested in processing form data.
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)
        # If the two forms are valid...
        if user_form.is_valid() and profile_form.is_valid():
            # Save the user's form data to the database.
            user = user_form.save()

            # Now we hash the password with the set_password method.
            # Once hashed, we can update the user object.
            user.set_password(user.password)
            user.save()

            # Now sort out the UserProfile instance.
            # Since we need to set the user attribute ourselves, we set commit=False.
            # This delays saving the model until we're ready to avoid integrity problems.
            profile = profile_form.save(commit=False)
            profile.user = user

            # Did the user provide a profile picture?
            # If so, we need to get it from the input form and put it in the UserProfile model.
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            # Now we save the UserProfile model instance.
            profile.save()

            # Update our variable to tell the template registration was successful.
            registered = True

        # Print form errors to the terminal.
        else:
            print user_form.errors, profile_form.errors

    # Not a HTTP POST, so we render our form using two ModelForm instances.
    # These forms will be blank, ready for user input.
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    return render_to_response(
            'soundmap/register.html',
            {'user_form': user_form, 'profile_form': profile_form, 'registered': registered},
            context)

def user_login(request):
	context = RequestContext(request)

	context_dict = {}

	if request.method== 'POST':
		username = request.POST['username']
		password = request.POST['password']

		user = authenticate(username=username, password=password)

		if user:
			if user.is_active:
				login(request, user)
				return HttpResponseRedirect('/soundmap/')
			else:
				context_dict['disabled_acct'] = True
				return render_to_response('soundmap/login.html', context_dict, context)
		else:
			#print "Invalid login details: {0}, {1}".format(username, password)
			#return HttpResponse("Invalid login details provided.")
			context_dict['bad_details']=True
			return render_to_response('soundmap/login.html', context_dict, context)
	else:
		return render_to_response('soundmap/login.html', context_dict, context)

def profile(request):
	context = RequestContext(request)
	profile = None
	context_dict={}
	if request.method=='GET':
		name= request.GET.get('name', None)

	if name:
		user = User.objects.get(username=name)
		if user:
			profile = UserProfile.objects.get(user=user)
			context_dict['username'] = profile.user.username
			context_dict['location'] = profile.location
			if profile.picture:
				context_dict['picture_url']=profile.picture.url
	return HttpResponse(simplejson.dumps(context_dict))

@login_required
def user_logout(request):
	logout(request)

	return HttpResponseRedirect('/soundmap/')

@login_required
def likeSong(request):
	context=RequestContext(request)
	song_id=None
	if request.method=='GET':
		song_id = request.GET['song_id']

	likes=0
	if song_id:
		song = Song.objects.get(id=int(song_id))
		if song:
			likes = song.likes+1
			song.likes = likes
			song.save()

	return HttpResponse(likes)

def updateListens(request):
	context= RequestContext(request)
	song_id=None
	if request.method=='GET':
		song_id = request.GET['song_id']
	listens=0
	if song_id:
		song = Song.objects.get(id=int(song_id))
		if song:
			listens = song.listens+1
			song.listens = listens
			song.save()
	return HttpResponse(listens)

#Function: getMarkerInfo
# -----------------------
# This function is used by an AJAJ GET request from loadmap.js. It returns
# a JSON object containing information (such as lat, lng) for all the playlists
# in the database. This information is then used to place the playlist markers on
# the map

def getMarkerInfo(request):
	context=RequestContext(request)
	if request.method=='GET':
		playlist_db = {} 	#JSON object containing all playlist markers
		all_playlists = Playlist.objects.all()
		if all_playlists:
			count =1
			for playlist in all_playlists:
				marker = {}
				marker['lat'] = playlist.latitude
				marker['lng'] = playlist.longitude
				marker['city'] = playlist.city
				playlist_db['playlist'+str(count)] = marker
				count +=1
		return HttpResponse(simplejson.dumps(playlist_db))

	else:
		return HttpResponseRedirect('/soundmap/')

def getPlaylistInfo(request):
	context=RequestContext(request)
	if request.method=='GET':
		song_db = {}	#JSON object containing all songs that are in the current playlist
		city = request.GET.get('city', None)
		if city:
			playlist = Playlist.objects.filter(city=city)
			if playlist:
				song_list = Song.objects.filter(playlist=playlist)
				count =1
				for song in song_list:
					marker = {}
					marker['name'] = song.name
					marker['artist'] = song.artist
					marker['url'] = song.url
					marker['id'] = song.id
					marker['username'] = song.uploader.user.username
					marker['likes'] = song.likes
					song_db['song'+str(count)] = marker
					count +=1
		return HttpResponse(simplejson.dumps(song_db))
	else:
		return HttpResponseRedirect('/soundmap/')