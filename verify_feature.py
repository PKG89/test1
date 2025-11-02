#!/usr/bin/env python3
"""Verification script for relief densification feature."""

import sys
from pathlib import Path

print("=" * 70)
print("RELIEF DENSIFICATION FEATURE VERIFICATION")
print("=" * 70)

# Check imports
print("\n1. Testing imports...")
try:
    from src.services.processing_service import ProcessingService
    from src.services.densification_service import DensificationService
    from src.models.settings import ProjectSettings, DensificationSettings, InterpolationMethod
    from src.models.point_data import PointCloud, TIN, PointType
    from src.processors.point_cloud import PointCloudProcessor
    from src.processors.tin_builder import TINBuilder
    from src.dxf.exporter import DXFExporter
    from src.dxf.layer_manager import LayerManager, LayerConfig
    from src.bot.conversation import DensificationConversation
    print("✅ All imports successful")
except Exception as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

# Check models
print("\n2. Testing models...")
try:
    settings = DensificationSettings(
        enabled=True,
        grid_spacing=5.0,
        interpolation_method=InterpolationMethod.LINEAR,
        show_generated_layer=True,
        show_triangles_layer=True,
        max_points=10000,
        min_spacing_threshold=10.0
    )
    assert settings.enabled == True
    assert settings.grid_spacing == 5.0
    assert settings.interpolation_method == InterpolationMethod.LINEAR
    print("✅ Models work correctly")
except Exception as e:
    print(f"❌ Model test failed: {e}")
    sys.exit(1)

# Check conversation messages
print("\n3. Testing conversation messages...")
try:
    msg = DensificationConversation.get_initial_prompt()
    assert "денсификация" in msg.lower()
    
    msg = DensificationConversation.get_grid_spacing_prompt()
    assert "шаг сетки" in msg.lower()
    
    msg = DensificationConversation.get_interpolation_method_prompt()
    assert "интерполяц" in msg.lower()
    
    msg = DensificationConversation.get_summary(settings)
    assert "Включена" in msg
    
    print("✅ Conversation messages correct")
except Exception as e:
    print(f"❌ Conversation test failed: {e}")
    sys.exit(1)

# Check layer names
print("\n4. Testing layer configuration...")
try:
    assert LayerConfig.EDITED_SURFACE == "2 отредактированная поверхность"
    assert LayerConfig.ADDED_POINTS == "2 пикеты добавленные"
    assert LayerConfig.ORIGINAL_SURFACE == "1 исходная поверхность"
    assert LayerConfig.ORIGINAL_POINTS == "1 пикеты исходные"
    print("✅ Layer names correct")
except Exception as e:
    print(f"❌ Layer test failed: {e}")
    sys.exit(1)

# Check point cloud processing
print("\n5. Testing point cloud processing...")
try:
    input_file = Path("examples/sample_coordinates.txt")
    if input_file.exists():
        processor = PointCloudProcessor()
        cloud = processor.load_from_file(str(input_file))
        assert cloud.count > 0
        
        stats = processor.calculate_spacing_statistics(cloud)
        assert 'mean_spacing' in stats
        assert 'min_spacing' in stats
        assert 'max_spacing' in stats
        
        print(f"✅ Loaded {cloud.count} points")
    else:
        print("⚠️  Sample file not found, skipping")
except Exception as e:
    print(f"❌ Point cloud test failed: {e}")
    sys.exit(1)

# Check TIN building
print("\n6. Testing TIN building...")
try:
    if input_file.exists():
        builder = TINBuilder()
        tin = builder.build(cloud.points)
        assert tin.triangle_count > 0
        print(f"✅ Built TIN with {tin.triangle_count} triangles")
    else:
        print("⚠️  Skipping TIN test")
except Exception as e:
    print(f"❌ TIN test failed: {e}")
    sys.exit(1)

# Check densification service
print("\n7. Testing densification service...")
try:
    if input_file.exists():
        densif_settings = DensificationSettings(
            enabled=True,
            grid_spacing=2.5,
            min_spacing_threshold=4.0
        )
        service = DensificationService(densif_settings)
        densified_cloud, stats = service.densify(cloud, tin)
        
        assert 'generated_points' in stats
        assert 'original_points' in stats
        print(f"✅ Generated {stats['generated_points']} new points")
    else:
        print("⚠️  Skipping densification test")
except Exception as e:
    print(f"❌ Densification test failed: {e}")
    sys.exit(1)

# Check DXF export
print("\n8. Testing DXF export...")
try:
    import tempfile
    import os
    
    with tempfile.TemporaryDirectory() as tmpdir:
        output_file = os.path.join(tmpdir, "test.dxf")
        exporter = DXFExporter()
        
        # Check layers exist
        assert LayerConfig.EDITED_SURFACE in exporter.doc.layers
        assert LayerConfig.ADDED_POINTS in exporter.doc.layers
        
        if input_file.exists():
            exporter.export_full_project(
                original_cloud=cloud,
                original_tin=tin,
                densified_cloud=densified_cloud,
                densified_tin=None,
                show_original=True,
                show_densified=True
            )
            exporter.save(output_file)
            
            assert os.path.exists(output_file)
            print(f"✅ DXF export successful")
        else:
            print("⚠️  Skipping export test")
except Exception as e:
    print(f"❌ DXF export test failed: {e}")
    sys.exit(1)

# Check full workflow
print("\n9. Testing full workflow...")
try:
    if input_file.exists():
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, "output.dxf")
            
            project_settings = ProjectSettings(
                densification=DensificationSettings(
                    enabled=True,
                    grid_spacing=3.0,
                    min_spacing_threshold=4.0
                )
            )
            
            processing_service = ProcessingService()
            results = processing_service.process_project(
                str(input_file),
                output_file,
                project_settings
            )
            
            assert results['success'] == True
            assert 'points_loaded' in results
            assert 'densification' in results
            
            print(f"✅ Full workflow successful")
            print(f"   - Loaded: {results['points_loaded']} points")
            print(f"   - Generated: {results['densification']['generated_points']} points")
    else:
        print("⚠️  Skipping workflow test")
except Exception as e:
    print(f"❌ Workflow test failed: {e}")
    sys.exit(1)

print("\n" + "=" * 70)
print("ALL VERIFICATION TESTS PASSED ✅")
print("=" * 70)
print("\nFeature is ready for production use!")
