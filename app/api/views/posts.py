from django.shortcuts import redirect, render
from django.contrib import messages

from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from api.models import Author, Post, Comment, visibility_type
from api.serializers import PostSerializer
from api.utils import methods, generate_id, invalid_user_view, author_not_found, post_not_found
from api.forms import NewPostForm

from datetime import datetime


class PostViewSet(viewsets.ViewSet):

    permission_classes = [permissions.IsAuthenticated]

    """
    URL: api/author/{authorID}/posts/
    GET: get recent posts of author (paginated)
    POST: create a new post but generate a postID
    """
    @action(methods=[methods.GET], detail=True)
    def get_author_posts(self, request, authorID):
        """ list author posts """
        # return 401 response if the author does not exists
        if author_not_found(authorID):
            return Response(status=status.HTTP_404_NOT_FOUND)

        # get all posts that is owned by the author
        author = Author.objects.filter(authorID=authorID)
        queryset = Post.objects.filter(
            author__in=author).order_by('-published')
        serializer = PostSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=[methods.POST], detail=True)
    def create_post_with_new_id(self, request, authorID):
        """ create a post """
        if author_not_found(authorID):
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            instance = Post(postID=generate_id())
            instance.author = Author.objects.get(authorID=authorID)
            self.populate_new_post_data(serializer.data, instance)
            self.populate_post_data(serializer.data, instance)
            return Response(PostSerializer(instance).data, status=status.HTTP_200_OK)
        else:
            # return 400 response if the data was invalid/missing require field
            return Response(status=status.HTTP_400_BAD_REQUEST)

    """
    URL: api/author/{authorID}/posts/{postID}
    GET: get a public post by postID
    POST: update the post (must be authenticated)
    DELETE: remove the author's post
    PUT: create a post with that postID
    """
    @action(methods=[methods.GET], detail=True)
    def get_public_post(self, request, authorID, postID):
        """ list public postS """
        if post_not_found(postID):
            return Response(status=status.HTTP_404_NOT_FOUND)

        queryset = Post.objects.filter(
            postID=postID, visibility=visibility_type.PUBLIC)
        serializer = PostSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=[methods.PUT], detail=True)
    def create_post_with_existing_id(self, request, authorID, postID):
        """ create a post """
        if not post_not_found(postID):
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if author_not_found(authorID):
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            instance = Post(postID=postID)
            instance.author = Author.objects.get(authorID=authorID)
            self.populate_new_post_data(serializer.data, instance)
            self.populate_post_data(serializer.data, instance)
            return Response(PostSerializer(instance).data, status=status.HTTP_200_OK)
        else:
            # return 400 response if the data was invalid/missing require field
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(methods=[methods.DELETE], detail=True)
    def delete_post(self, request, authorID, postID):
        if author_not_found(authorID) or post_not_found(postID):
            return Response(status=status.HTTP_404_NOT_FOUND)

        Post.objects.get(postID=postID).delete()
        return Response(status=status.HTTP_200_OK)

    @action(methods=[methods.POST], detail=True)
    def update_post(self, request, authorID, postID):
        if author_not_found(authorID) or post_not_found(postID):
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            instance = Post.objects.get(postID=postID)
            self.populate_post_data(serializer.data, instance)
            return Response(PostSerializer(instance).data, status=status.HTTP_200_OK)
        else:
            # return 400 response if the data was invalid/missing require field
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def populate_post_data(self, data, instance):
        """ put request data into instance 
        auto-set fields: type, postID, author, 
            visibility(?), unlisted(?), source(?), origin(?), count(?), likes(?)

        example of an working data:

        {
        "title": "my title",
        "description": "my des",
        "content": "my content",
        "categories": ["web", "tutorial"]
        }

        """

        instance.title = data["title"]
        instance.description = data["description"]
        instance.content = data["content"]
        instance.categories = data["categories"]
        # instance.count = len(data["comment"])  # total number of comments for this post
        instance.save()

    def populate_new_post_data(self, data, instance):
        """ put request data into instance 
        auto-set fields: postID, type, visibility, unlisted, count

        example of an working data:

        {
        "title": "my title",
        "source": "https://uofa-cmput404.github.io/",
        "origin": "https://uofa-cmput404.github.io/",
        "description": "my des",
        "contentType": "text/plain",
        "content": "my content",
        "categories": ["web", "tutorial"],
        "visibility": "PUBLIC",
        "unlisted": false
        }

        """

        instance.source = data["source"]  # TODO make it to url
        instance.origin = data["origin"]  # TODO make it to url
        instance.contentType = data["contentType"]
        instance.published = datetime.now().isoformat()
        instance.visibility = data["visibility"]
        instance.unlisted = data["unlisted"]
        instance.save()


# View of post
def post_handler(request, authorID):
    # Check the user is invalid in view
    if invalid_user_view(request):
        return redirect("login")

    # Check the author is exist and the current user is the same author
    if authorID != str(request.user.author.authorID):
        messages.error(request, "Error. Unexpected user.")
        return redirect("logout")

    # When the request method is POST
    if request.method == "POST":
        # PUT - create a post with generate post_id
        if request.POST.get("myCustom_method") == "PUT":
            form = NewPostForm(request.POST)
            if form.is_valid():
                instance = Post(postID=generate_id())
                instance.author = Author.objects.get(authorID=authorID)
                populate_post_data(form.cleaned_data, instance)
                messages.info(
                    request, "Congratulations! Your post has been published.")
            else:
                messages.error(
                    request, "Unsuccessful published. Invalid information.")

            return redirect("homepage")

        # GET, POST, DELETE
        else:
            try:
                postID = request.POST.get("myCustom_postID")
                current_post = Post.objects.filter(postID=postID).first()

                # GET - get the public post
                if request.POST.get("myCustom_method") == "GET":
                    pass

                # POST - update the post
                elif request.POST.get("myCustom_method") == "POST":
                    form = NewPostForm(request.POST, instance=current_post)
                    if form.is_valid():
                        form.save()
                        messages.info(
                            request, f"Your post {postID} has been update.")
                    else:
                        messages.error(
                            request, "Unsuccessful update. Invalid information.")

                # DELETE - remove the post
                elif request.POST.get("myCustom_method") == "DELETE":
                    current_post.delete()
                    messages.info(
                        request, f"Your post {postID} has been deleted.")

            except:
                messages.error(request, "Unexpected error...")

            return redirect("my-posts")

    # When the request method is GET
    elif request.method == "GET":
        return redirect("my-posts")

    else:
        return Response(status=status.HTTP_404_NOT_FOUND)


def populate_post_data(data, instance):
    """ put request data into instance 
    example of an working data:

    {
    "title": "my title",
    "source": "https://uofa-cmput404.github.io/",
    "origin": "https://uofa-cmput404.github.io/",
    "description": "my des",
    "contentType": "text/plain",
    "content": "my content",
    "categories": ["web", "tutorial"]
    }

    """

    instance.title = data["title"]
    # DO NOT REMOVE uncomment field in this method
    # instance.source = data["source"]  # TODO make it to url
    # nstance.origin = data["origin"]  # TODO make it to url
    instance.description = data["description"]
    # instance.contentType = data["contentType"]
    instance.content = data["content"]
    instance.categories = data["categories"]
    instance.published = datetime.now().isoformat()
    instance.save()

# View of my posts


def my_posts_view(request):
    # Check the user is invalid in view
    if invalid_user_view(request):
        return redirect("login")

    content = {}

    self_post = Post.objects.filter(
        author__exact=request.user.author).order_by('-published')

    content['self_post'] = self_post
    content['my_posts_page'] = True

    return render(request, "my_posts.html", content)
