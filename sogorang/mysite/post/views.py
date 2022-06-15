from django.shortcuts import render,redirect
from django.db.models import Q
from home.models import *

def deal_com(request,post_id):
  if request.method == 'POST' :
    post = Post.objects.get(postPIN=post_id)
    post.dealStatus=2
    post.buyer=request.user.username
    post.save()
    return redirect('/chat/'+str(post.postPIN)+'/delete')



def req_deal(request,post_id) :
  post = Post.objects.get(postPIN=post_id)
  post.dealStatus=1
  post.buyer=request.user.username
  post.save()
  return redirect('/chat/'+str(post.postPIN)+'/'+str(0))


#검색 기능
def get_search(request):
  selectList=['createTime','price','viewCount']

  if request.method=="GET":
    keyWord=request.GET.get('keyWord','')
    select1=request.GET.get('selectbox','')
    select2=request.GET.get('selectbox2','')

    productList = Data.objects.all()
    product = productList.filter(Q(name__icontains = keyWord))

#기본 검색을 하거나. 카테고리를 통한 검색
    if(select1 or select2):
      
      postList = Post.objects.all()
      if(select2.isdigit()):
        searchList = postList.filter(Q(title__icontains = keyWord)|Q(productName__icontains = keyWord)&Q(category=select2))
      else:
        searchList = postList.filter(Q(title__icontains = keyWord)|Q(productName__icontains = keyWord))

      if(select1.isdigit()):
        searchList = searchList.order_by(selectList[int(select1)])
        
      context = {'searchList':searchList,  'product':product}

      return render(request, 'post/search.html', context)
    
    else:
      keyWord = request.GET['keyWord']
      postList = Post.objects.all()

      searchList = postList.filter(Q(title__icontains = keyWord)|Q(productName__icontains = keyWord)).order_by('createTime').reverse()

      context = {'searchList':searchList,  'product':product}

      return render(request, 'post/search.html', context)


def post_send(request):
  if request.method=='POST':
    post = Post()
    post.seller = request.user.username
    post.category = request.POST['category']
    post.productName = request.POST['productName']
    post.title = request.POST['title']
    post.content= request.POST['description']
    post.status = request.POST['condition']
    post.viewCount = 0

    post.price = request.POST['unitPrice']
    post.image = request.FILES['productImage']
    post.dealStatus = 0
    post.latitude=request.POST['sel_latitude']
    post.longitude=request.POST['sel_longitude']
    post.dealAddress=request.POST['sel_address']
    post.productPIN=request.POST['productPIN']
    post.save()
  return redirect('/')

def post_create(request):
  data = Data.objects.all()
  content={'data':data}
  return render(request, 'post/createPost.html', content)

def post_detail(request, post_id):
  if(Post.objects.filter(postPIN = post_id).exists()):
    data= Post.objects.get(postPIN=post_id)
    if(request.user.is_authenticated):
      category = data.category
      request.user.cg_views[category]+=1
      request.user.save()
    content = {'data':data}

  return render(request, 'post/postDescription.html',content)

#포스트 수정
def post_edit(request,post_id):
  if request.method=='GET':
    data = Post.objects.get(postPIN=post_id)
    post = Data.objects.all()
    content={'post':post, 'data':data}
    return render(request, 'post/editPost.html',content)

  if request.method=='POST':
    post= Post.objects.get(postPIN=post_id)
    if request.FILES['productImage'] is not None :
      post.image = request.FILES['productImage']
    post.category = request.POST['category']
    post.productName = request.POST['productName']
    post.title = request.POST['title']
    post.content= request.POST['content']
    post.status = request.POST['status']
    post.viewCount = 0
    post.price = request.POST['unitPrice']
    post.dealStatus = 0
    post.latitude=request.POST['sel_latitude']
    post.longitude=request.POST['sel_longitude']
    post.dealAddress=request.POST['sel_address']
    post.productPIN=request.POST['productPIN']
    post.save()
    return redirect('/post/'+str(post.postPIN))

def post_delete(request, post_id):
  data = Post.objects.get(postPIN=post_id)
  data.delete()
  return redirect('/')


def product_category(request, param):
  data= Data.objects.get(productPIN=param)
  postList= Post.objects.filter(productPIN = param)
  content = {'data':data, 'postList':postList}

  return render(request, 'post/data.html',content)