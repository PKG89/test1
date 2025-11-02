"""Dependency injection container for CAD-P bot services."""

from typing import Optional
from .config import config


class ServiceContainer:
    """
    Simple dependency injection container for managing service instances.
    
    This provides a centralized place to instantiate and access services,
    making it easy to swap implementations and manage dependencies.
    """
    
    def __init__(self):
        self._services = {}
        self._config = config
    
    def register(self, name: str, service):
        """Register a service instance."""
        self._services[name] = service
    
    def get(self, name: str):
        """Get a registered service instance."""
        return self._services.get(name)
    
    def has(self, name: str) -> bool:
        """Check if a service is registered."""
        return name in self._services
    
    @property
    def config(self):
        """Get configuration instance."""
        return self._config
    
    def initialize_services(self):
        """
        Initialize and register all application services.
        
        This method is called during application startup to set up
        all required services with their dependencies.
        """
        # Import services lazily to avoid circular imports
        from .services.processing_service import ProcessingService
        from .services.tin_service import TINService
        from .services.densification_service import DensificationService
        from .services.rule_engine import RuleEngine
        from .services.catalog_workflow import CatalogWorkflow
        
        # Register services
        self.register("tin_service", TINService())
        self.register("densification_service", DensificationService())
        self.register("rule_engine", RuleEngine())
        self.register("catalog_workflow", CatalogWorkflow())
        self.register("processing_service", ProcessingService())
    
    def get_processing_service(self):
        """Get the processing service instance."""
        if not self.has("processing_service"):
            self.initialize_services()
        return self.get("processing_service")
    
    def get_tin_service(self):
        """Get the TIN service instance."""
        if not self.has("tin_service"):
            self.initialize_services()
        return self.get("tin_service")
    
    def get_densification_service(self):
        """Get the densification service instance."""
        if not self.has("densification_service"):
            self.initialize_services()
        return self.get("densification_service")
    
    def get_rule_engine(self):
        """Get the rule engine instance."""
        if not self.has("rule_engine"):
            self.initialize_services()
        return self.get("rule_engine")
    
    def get_catalog_workflow(self):
        """Get the catalog workflow instance."""
        if not self.has("catalog_workflow"):
            self.initialize_services()
        return self.get("catalog_workflow")


# Global service container instance
container = ServiceContainer()
