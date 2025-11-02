"""Main processing service orchestrating all operations."""

from typing import Dict, Any, Optional
from pathlib import Path

from src.processors.point_cloud import PointCloudProcessor
from src.processors.tin_builder import TINBuilder
from src.services.densification_service import DensificationService
from src.services.tin_service import TINService
from src.dxf.exporter import DXFExporter
from src.models.settings import ProjectSettings, DensificationSettings
from src.models.point_data import PointCloud, TIN


class ProcessingService:
    """Main service for processing geospatial data."""
    
    def __init__(self):
        """Initialize processing service."""
        self.point_processor = PointCloudProcessor()
    
    def process_project(self, 
                       data_file: str,
                       output_file: str,
                       settings: ProjectSettings) -> Dict[str, Any]:
        """
        Process complete project from input file to DXF output.
        
        Args:
            data_file: Path to input coordinate file
            output_file: Path to output DXF file
            settings: Project settings including densification options
            
        Returns:
            Dictionary with processing statistics and results
        """
        results = {
            'success': False,
            'data_file': data_file,
            'output_file': output_file
        }
        
        try:
            cloud = self.point_processor.load_from_file(data_file)
            cloud = self.point_processor.remove_duplicates(cloud)
            cloud = self.point_processor.filter_outliers(cloud)
            results['points_loaded'] = cloud.count
            
            spacing_stats = self.point_processor.calculate_spacing_statistics(cloud)
            results['spacing_stats'] = spacing_stats
            
            tin_builder = TINBuilder()
            original_tin = tin_builder.build(cloud.points)
            results['original_triangles'] = original_tin.triangle_count
            results['tin_quality'] = original_tin.quality
            
            real_tin = None
            tin_stats = {}
            
            if settings.tin.enabled:
                tin_service = TINService(settings.tin)
                real_tin, tin_stats = tin_service.build_tin(cloud)
                results['real_tin'] = tin_stats
            
            densified_cloud = None
            densified_tin = None
            densification_stats = {}
            
            if settings.densification.enabled:
                densification_service = DensificationService(settings.densification)
                densified_cloud, densification_stats = densification_service.densify(
                    cloud, original_tin
                )
                results['densification'] = densification_stats
                
                if densification_stats['generated_points'] > 0:
                    densified_tin = tin_builder.build(densified_cloud.points)
                    results['densified_triangles'] = densified_tin.triangle_count
            
            exporter = DXFExporter(settings.template_path)
            
            show_densified = (
                settings.densification.enabled and 
                densified_cloud is not None and
                (settings.densification.show_generated_layer or 
                 settings.densification.show_triangles_layer)
            )
            
            show_real_tin = (
                settings.tin.enabled and 
                settings.tin.output_layers and
                real_tin is not None and
                not tin_stats.get('skipped', False)
            )
            
            exporter.export_full_project(
                original_cloud=cloud,
                original_tin=original_tin,
                densified_cloud=densified_cloud,
                densified_tin=densified_tin,
                real_tin=real_tin,
                show_original=True,
                show_densified=show_densified,
                show_real_tin=show_real_tin
            )
            
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            exporter.save(str(output_path))
            
            results['success'] = True
            results['output_path'] = str(output_path)
            
        except Exception as e:
            results['error'] = str(e)
            results['success'] = False
        
        return results
    
    def get_file_statistics(self, data_file: str) -> Dict[str, Any]:
        """
        Get statistics about input file without full processing.
        
        Args:
            data_file: Path to input coordinate file
            
        Returns:
            Dictionary with file statistics
        """
        try:
            cloud = self.point_processor.load_from_file(data_file)
            
            bounds = cloud.bounds
            spacing_stats = self.point_processor.calculate_spacing_statistics(cloud)
            
            return {
                'success': True,
                'point_count': cloud.count,
                'bounds': {
                    'min_x': bounds[0],
                    'max_x': bounds[1],
                    'min_y': bounds[2],
                    'max_y': bounds[3],
                    'min_z': bounds[4],
                    'max_z': bounds[5]
                },
                'spacing': spacing_stats
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
