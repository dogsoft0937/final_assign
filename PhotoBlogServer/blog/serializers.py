from blog.models import Post
from rest_framework import serializers
from django.contrib.auth.models import User

class PostSerializer(serializers.HyperlinkedModelSerializer):
    author = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    
    class Meta:
        model = Post
        fields = ['author', 'title', 'text', 'created_date', 'published_date', 'image']
        
    def create(self, validated_data):
        print("Received Data:", validated_data)
        # 좌표값 파싱 제거 - views.py에서 처리
        post = Post.objects.create(**validated_data)
        return post