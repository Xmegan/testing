from django.shortcuts import render, redirect, get_object_or_404
from django.views import generic
from django.utils import timezone
from django.urls import reverse_lazy, reverse
from .models import Post, Contact
from .forms import PostForm, ContactForm
from .filters import PostFilter
from django.contrib.auth.models import User
from django.shortcuts import  render, redirect
from .forms import NewUserForm
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponseRedirect, HttpResponse
from django.core.mail import send_mail, BadHeaderError

# Contacting Us 
def contact(request):
	if request.method == 'POST':
		form = ContactForm(request.POST)
		if form.is_valid():
			subject = "Website Inquiry" 
			body = {
			'first_name': form.cleaned_data['first_name'], 
			'last_name': form.cleaned_data['last_name'], 
			'email': form.cleaned_data['email_address'], 
			'message':form.cleaned_data['message'], 
			}
			message = "\n".join(body.values())

			try:
				send_mail(subject, message, 'meganli@hawaii.edu', ['meganli@hawaii.edu']) 
			except BadHeaderError:
				return HttpResponse('Invalid header found.')
			return redirect ("post_list")
      
	form = ContactForm()
	return render(request, "blogs/contact.html", {'form':form})

def LikeView(request,pk):
    post = get_object_or_404(Post, pk = pk)
    post.likes.add(request.user)
    return HttpResponseRedirect(request.META['HTTP_REFERER'])

def DislikeView(request, pk):
    post = get_object_or_404(Post, pk = pk)
    post.dislikes.add(request.user)
    return HttpResponseRedirect(request.META['HTTP_REFERER'])

# Register an account
def register_request(request):
	if request.method == "POST":
		form = NewUserForm(request.POST)
		if form.is_valid():
			user = form.save()
			login(request, user)
			messages.success(request, "Registration successful." )
			return redirect("post_list")
		messages.error(request, "Unsuccessful registration. Invalid information.")
	form = NewUserForm()
	return render (request=request, template_name="blogs/register.html", context={"register_form":form})

# Login user
def login_request(request):
	if request.method == "POST":
		form = AuthenticationForm(request, data=request.POST)
		if form.is_valid():
			username = form.cleaned_data.get('username')
			password = form.cleaned_data.get('password')
			user = authenticate(username=username, password=password)
			if user is not None:
				login(request, user)
				messages.info(request, "You are now logged in as {username}.")
				return redirect("post_list")
			else:
				messages.error(request,"Invalid username or password.")
		else:
			messages.error(request,"Invalid username or password.")
	form = AuthenticationForm()
	return render(request=request, template_name="blogs/login.html", context={"login_form":form})

# Logout user
def logout_request(request):
	logout(request)
	messages.info(request, "You have successfully logged out.") 
	return redirect("post_list")

class IndexView(generic.ListView):
    template_name = 'blogs/index.html'
    context_object_name = 'blogs_list'

    def get_queryset(self):
        """Return all the blogs."""
        return Post.objects.all()

def post_list(request):
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
    context = {
        'posts' : posts, 
    }
    return render(request, 'blogs/post_list.html', context)


def post_details(request, pk):
    post = get_object_or_404(Post, pk=pk)
    is_liked = False
    context = { 
        'post' : post,
        'is_liked' : is_liked,
        'total_likes': post.total_likes(),
        'total_dislikes': post.total_dislikes(),
    }
    return render(request, 'blogs/post_detail.html', context)

def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('post_list')
    else:
        form = PostForm()
    return render(request, 'blogs/post_new.html', {'form': form})

def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
        return redirect('post_list')
    else:
        form = PostForm(instance=post)
    return render(request, 'blogs/post_edit.html', {'form': form})

class SearchView(generic.ListView):
    template_name = 'blogs/search.html'
    context_object_name = 'blogs_list'

    def get_queryset(self):
        """Return all the blogs."""
        return Post.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = PostFilter(self.request.GET, queryset=self.get_queryset())
        return context

class UpdateView(generic.edit.UpdateView):
    template_name = 'blogs/update.html'
    model = Post
    fields = ['text', 'title']
    success_url = reverse_lazy('post_list')

class DeleteView(generic.edit.DeleteView):
    template_name = 'blogs/delete.html'
    model = Post
    success_url = reverse_lazy('post_list')

class OrderDateView(generic.ListView):
    template_name = 'blogs/ordering.html'
    context_object_name = 'blogs_list'

    def get_queryset(self):
        """Return all the blogs."""
        return Post.objects.order_by('-published_date')

class TodayView(generic.ListView):
    template_name = 'blogs/latest.html'
    context_object_name = 'blogs_list'

    def get_queryset(self):
        """Return all the blogs."""
        return Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')

class AboutViews(generic.ListView):
    template_name = 'blogs/aboutme.html'
    context_object_name = 'about'
    
    def get_queryset(self):
        """Return all the blogs."""
        return Post.objects.all()