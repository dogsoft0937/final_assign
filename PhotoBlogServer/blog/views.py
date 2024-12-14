from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from rest_framework import viewsets, permissions
from .models import Post, CongestionData
from .forms import PostForm
from .serializers import PostSerializer
from django.db.models import Avg, Count
from django.db.models.functions import ExtractHour
from django.contrib.auth.models import User


class blogImage(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        text = self.request.data.get('text', '')
        author_id = self.request.data.get('author', 1)
        author = User.objects.get(id=author_id)
        
        # person count 추출
        if '감지된 사람 수:' in text:
            count_str = text.split('감지된 사람 수:')[1].split('명')[0].strip()
            try:
                person_count = int(count_str)
                
                # 혼잡도 레벨 계산
                def get_congestion_level(count):
                    if count < 10:
                        return "여유"
                    elif count < 20:
                        return "보통"
                    else:
                        return "혼잡"
                
                congestion_level = get_congestion_level(person_count)
                
                # CongestionData 생성 및 저장
                congestion = CongestionData(
                    person_count=person_count,
                    congestion_level=congestion_level
                )
                congestion.save()
                
                # 원본 텍스트에 혼잡도 정보 추가
                text = f"{text} - 혼잡도: {congestion_level}"
                
            except ValueError as e:
                print(f"사람 수 파싱 오류: {e}")
                print(f"원본 텍스트: {text}")
                
        serializer.save(author=author, text=text)


def post_list(request):
    posts = Post.objects.order_by('published_date')
    return render(request, 'blog/post_list.html', {'posts': posts})


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'blog/post_detail.html', {'post': post})


def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'blog/post_edit.html', {'form': form})


def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/post_edit.html', {'form': form})


def congestion_analysis(request):
    # 시간대별 통계
    hourly_stats = CongestionData.objects.annotate(
        hour=ExtractHour('timestamp')
    ).values('hour').annotate(
        avg_count=Avg('person_count'),
        total_records=Count('id')
    ).order_by('hour')
    
    # 현재 혼잡도
    latest_data = CongestionData.objects.order_by('-timestamp').first()
    
    return render(request, 'blog/congestion_analysis.html', {
        'hourly_stats': hourly_stats,
        'current_congestion': latest_data,
    })