"""
Base Repository - Abstract base class for all repositories
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from django.db import models
from asgiref.sync import sync_to_async


class BaseRepository(ABC):
    """
    Abstract base repository class
    """
    
    def __init__(self, model_class: models.Model):
        self.model_class = model_class
    
    async def create(self, **kwargs) -> models.Model:
        """Create a new instance"""
        instance = self.model_class(**kwargs)
        await sync_to_async(instance.save, thread_sensitive=True)()
        return instance
    
    async def get_by_id(self, instance_id: int) -> Optional[models.Model]:
        """Get instance by ID"""
        try:
            return await sync_to_async(
                self.model_class.objects.get
            )(id=instance_id)
        except self.model_class.DoesNotExist:
            return None
    
    async def get_all(self, limit: int = 100) -> List[models.Model]:
        """Get all instances with optional limit"""
        queryset = self.model_class.objects.all()[:limit]
        return await sync_to_async(list)(queryset)
    
    async def update(self, instance: models.Model, **kwargs) -> models.Model:
        """Update an existing instance"""
        for key, value in kwargs.items():
            setattr(instance, key, value)
        await sync_to_async(instance.save, thread_sensitive=True)()
        return instance
    
    async def delete(self, instance: models.Model) -> bool:
        """Delete an instance"""
        try:
            await sync_to_async(instance.delete, thread_sensitive=True)()
            return True
        except Exception:
            return False
    
    async def filter(self, **kwargs) -> List[models.Model]:
        """Filter instances by criteria"""
        queryset = self.model_class.objects.filter(**kwargs)
        return await sync_to_async(list)(queryset)
    
    async def count(self, **kwargs) -> int:
        """Count instances matching criteria"""
        queryset = self.model_class.objects.filter(**kwargs)
        return await sync_to_async(queryset.count)()
    
    async def exists(self, **kwargs) -> bool:
        """Check if instance exists with criteria"""
        queryset = self.model_class.objects.filter(**kwargs)
        return await sync_to_async(queryset.exists)()