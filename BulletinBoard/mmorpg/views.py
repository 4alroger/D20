from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, UpdateView, DeleteView, CreateView
from django.contrib.auth.decorators import login_required
from .models import Post, Reply
from .forms import ReplyForm, PostForm
from .filters import PostFilter
from django.views.generic.edit import FormMixin


class PostList(ListView):
    model = Post
    ordering = '-time_create'
    template_name = 'posts.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = PostFilter(self.request.GET, queryset)
        return self.filterset.qs


class PostDetail(FormMixin, DetailView):
    model = Post
    template_name = 'post.html'
    form_class = ReplyForm
    context_object_name = 'post'

    def get_success_url(self):
        return reverse('post', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        comments = Reply.objects.filter(accepted=True, post_id=self.kwargs['pk']).order_by('time_create')
        context['comments'] = comments

        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            reply = form.save(commit=False)
            reply.post = self.object
            reply.user = self.request.user
            reply.send_notification_email()
            reply.save()
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class ReplyDetail(DetailView):
    model = Reply
    template_name = 'reply.html'
    context_object_name = 'reply'


class ReplyList(ListView):
    model = Reply
    template_name = 'replies.html'
    ordering = '-time_create'
    context_object_name = 'replies'


class PostDetailUser(LoginRequiredMixin, DetailView):
    model = Post
    template_name = 'post_user.html'
    context_object_name = 'post_user'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        comments = Reply.objects.filter(accepted=True, post_id=self.kwargs['pk']).order_by('time_create')
        context['comments'] = comments

        return context


class PostCreate(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'post_edit.html'

    def form_valid(self, form):
        self.object = form.save(commit=False)
        current_user = self.request.user
        self.object.user = current_user
        return super().form_valid(form)


class ReplyCreate(LoginRequiredMixin, CreateView):
    model = Reply
    form_class = ReplyForm
    template_name = 'reply_edit.html'

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.post = Post.objects.get(pk=self.kwargs['pk'])
        current_user = self.request.user
        self.object.user = current_user
        return super().form_valid(form)


class PostUpdate(LoginRequiredMixin, UpdateView):
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'
    success_url = reverse_lazy('user_posts')


class PostDelete(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('user_posts')


class ReplyDelete(LoginRequiredMixin, DeleteView):
    model = Reply
    template_name = 'reply_delete.html'
    success_url = reverse_lazy('user_replies')


@login_required
def user_posts(request):
    current_user = request.user
    posts = Post.objects.filter(user=current_user).order_by('-time_create')
    return render(request, 'user_posts.html', {'posts': posts})


@login_required
def user_replies(request):
    current_user = request.user
    posts = Post.objects.filter(user=current_user).order_by('-time_create')
    selected_post_id = request.GET.get('post')

    replies = Reply.objects.filter(post__user=current_user).order_by('-time_create')
    if selected_post_id:
        replies = replies.filter(post__id=selected_post_id)

    if request.method == 'GET':
        selected_post_id = request.GET.get('post')
        if selected_post_id:
            replies = replies.filter(post__id=selected_post_id)

    return render(request, 'user_replies.html',
                  {'posts': posts, 'replies': replies, 'selected_post_id': selected_post_id})


@login_required
def accept_reply(request, pk):
    reply = get_object_or_404(Reply, pk=pk)
    reply.accepted = True
    reply.save()
    reply.send_accepted_email()
    return HttpResponseRedirect(reverse('user_replies'))