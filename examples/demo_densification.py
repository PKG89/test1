#!/usr/bin/env python3
"""Demo script for relief densification feature."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.processing_service import ProcessingService
from src.models.settings import ProjectSettings, DensificationSettings, InterpolationMethod
from src.bot.conversation import DensificationConversation


def demo_basic_densification():
    """Demonstrate basic densification."""
    print("=" * 70)
    print("DEMO 1: Basic Densification")
    print("=" * 70)
    
    input_file = Path(__file__).parent / "sample_coordinates.txt"
    output_file = Path(__file__).parent.parent / "output" / "demo_basic.dxf"
    
    settings = ProjectSettings(
        scale=1.0,
        densification=DensificationSettings(
            enabled=True,
            grid_spacing=2.5,
            interpolation_method=InterpolationMethod.LINEAR,
            show_generated_layer=True,
            show_triangles_layer=True
        )
    )
    
    print("\n📋 Settings:")
    print(DensificationConversation.get_summary(settings.densification))
    
    service = ProcessingService()
    print("\n⚙️ Processing...")
    results = service.process_project(str(input_file), str(output_file), settings)
    
    if results['success']:
        print("\n✅ Success!")
        print(f"Points loaded: {results['points_loaded']}")
        if 'densification' in results:
            print(DensificationConversation.get_processing_message(results['densification']))
        print(f"\n📁 Output: {results['output_path']}")
    else:
        print(f"\n❌ Error: {results.get('error')}")
    
    print()


def demo_interpolation_methods():
    """Demonstrate different interpolation methods."""
    print("=" * 70)
    print("DEMO 2: Interpolation Methods Comparison")
    print("=" * 70)
    
    input_file = Path(__file__).parent / "sample_coordinates.txt"
    output_dir = Path(__file__).parent.parent / "output"
    
    methods = [
        (InterpolationMethod.LINEAR, "linear"),
        (InterpolationMethod.CUBIC, "cubic"),
        (InterpolationMethod.NEAREST, "nearest")
    ]
    
    service = ProcessingService()
    
    for method, name in methods:
        print(f"\n--- Testing {name.upper()} interpolation ---")
        
        output_file = output_dir / f"demo_{name}.dxf"
        
        settings = ProjectSettings(
            scale=1.0,
            densification=DensificationSettings(
                enabled=True,
                grid_spacing=2.5,
                interpolation_method=method
            )
        )
        
        results = service.process_project(str(input_file), str(output_file), settings)
        
        if results['success']:
            print(f"✓ {name}: Generated {results['densification']['generated_points']} points")
        else:
            print(f"✗ {name}: {results.get('error')}")
    
    print()


def demo_grid_spacing_comparison():
    """Demonstrate different grid spacing values."""
    print("=" * 70)
    print("DEMO 3: Grid Spacing Comparison")
    print("=" * 70)
    
    input_file = Path(__file__).parent / "sample_coordinates.txt"
    output_dir = Path(__file__).parent.parent / "output"
    
    spacings = [2.0, 3.0, 5.0, 10.0]
    
    service = ProcessingService()
    
    for spacing in spacings:
        print(f"\n--- Grid spacing: {spacing} m ---")
        
        output_file = output_dir / f"demo_spacing_{spacing}.dxf"
        
        settings = ProjectSettings(
            scale=1.0,
            densification=DensificationSettings(
                enabled=True,
                grid_spacing=spacing
            )
        )
        
        results = service.process_project(str(input_file), str(output_file), settings)
        
        if results['success']:
            points = results['densification']['generated_points']
            original = results['points_loaded']
            percentage = (points / original * 100) if original > 0 else 0
            print(f"✓ Generated {points} points (+{percentage:.0f}%)")
        else:
            print(f"✗ Error: {results.get('error')}")
    
    print()


def demo_layer_visibility():
    """Demonstrate layer visibility options."""
    print("=" * 70)
    print("DEMO 4: Layer Visibility Options")
    print("=" * 70)
    
    input_file = Path(__file__).parent / "sample_coordinates.txt"
    output_dir = Path(__file__).parent.parent / "output"
    
    configs = [
        (True, True, "both"),
        (True, False, "points_only"),
        (False, True, "triangles_only")
    ]
    
    service = ProcessingService()
    
    for show_points, show_triangles, name in configs:
        print(f"\n--- {name.replace('_', ' ').title()} ---")
        
        output_file = output_dir / f"demo_layers_{name}.dxf"
        
        settings = ProjectSettings(
            scale=1.0,
            densification=DensificationSettings(
                enabled=True,
                grid_spacing=3.0,
                show_generated_layer=show_points,
                show_triangles_layer=show_triangles
            )
        )
        
        results = service.process_project(str(input_file), str(output_file), settings)
        
        if results['success']:
            print(f"✓ Created with:")
            print(f"  - Generated points layer: {'ON' if show_points else 'OFF'}")
            print(f"  - Triangles layer: {'ON' if show_triangles else 'OFF'}")
        else:
            print(f"✗ Error: {results.get('error')}")
    
    print()


def demo_file_statistics():
    """Demonstrate file statistics retrieval."""
    print("=" * 70)
    print("DEMO 5: File Statistics")
    print("=" * 70)
    
    input_file = Path(__file__).parent / "sample_coordinates.txt"
    
    service = ProcessingService()
    stats = service.get_file_statistics(str(input_file))
    
    if stats['success']:
        print("\n📊 File Information:")
        print(f"  Total points: {stats['point_count']}")
        print(f"\n📏 Spatial Extent:")
        print(f"  X: {stats['bounds']['min_x']:.3f} to {stats['bounds']['max_x']:.3f}")
        print(f"  Y: {stats['bounds']['min_y']:.3f} to {stats['bounds']['max_y']:.3f}")
        print(f"  Z: {stats['bounds']['min_z']:.3f} to {stats['bounds']['max_z']:.3f}")
        print(f"\n📐 Point Spacing:")
        print(f"  Mean: {stats['spacing']['mean_spacing']:.3f} m")
        print(f"  Min: {stats['spacing']['min_spacing']:.3f} m")
        print(f"  Max: {stats['spacing']['max_spacing']:.3f} m")
        print(f"  Median: {stats['spacing']['median_spacing']:.3f} m")
    else:
        print(f"❌ Error: {stats.get('error')}")
    
    print()


def demo_all():
    """Run all demos."""
    print("\n" + "=" * 70)
    print("DXF GEO-PROCESSING: RELIEF DENSIFICATION DEMOS")
    print("=" * 70 + "\n")
    
    demos = [
        demo_basic_densification,
        demo_interpolation_methods,
        demo_grid_spacing_comparison,
        demo_layer_visibility,
        demo_file_statistics
    ]
    
    for demo in demos:
        try:
            demo()
        except Exception as e:
            print(f"\n❌ Demo failed: {e}\n")
    
    print("=" * 70)
    print("All demos completed!")
    print("=" * 70)


if __name__ == '__main__':
    demo_all()
