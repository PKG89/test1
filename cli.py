#!/usr/bin/env python3
"""Command-line interface for DXF geo-processing."""

import argparse
import sys
from pathlib import Path

from src.services.processing_service import ProcessingService
from src.models.settings import ProjectSettings, DensificationSettings, InterpolationMethod
from src.bot.conversation import DensificationConversation


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="DXF Geo-processing with relief densification"
    )
    
    parser.add_argument(
        'input_file',
        type=str,
        help='Input coordinate file (.txt or .xyz)'
    )
    
    parser.add_argument(
        'output_file',
        type=str,
        help='Output DXF file'
    )
    
    parser.add_argument(
        '--densify',
        action='store_true',
        help='Enable relief densification'
    )
    
    parser.add_argument(
        '--grid-spacing',
        type=float,
        default=5.0,
        help='Grid spacing for densification (default: 5.0 m)'
    )
    
    parser.add_argument(
        '--interpolation',
        type=str,
        choices=['linear', 'cubic', 'nearest'],
        default='linear',
        help='Interpolation method (default: linear)'
    )
    
    parser.add_argument(
        '--max-points',
        type=int,
        default=10000,
        help='Maximum number of generated points (default: 10000)'
    )
    
    parser.add_argument(
        '--min-spacing',
        type=float,
        default=10.0,
        help='Minimum spacing threshold for densification (default: 10.0 m)'
    )
    
    parser.add_argument(
        '--show-generated',
        action='store_true',
        default=True,
        help='Show generated points layer'
    )
    
    parser.add_argument(
        '--show-triangles',
        action='store_true',
        default=True,
        help='Show triangles layer'
    )
    
    parser.add_argument(
        '--stats',
        action='store_true',
        help='Show file statistics only'
    )
    
    args = parser.parse_args()
    
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"Error: Input file not found: {args.input_file}", file=sys.stderr)
        return 1
    
    service = ProcessingService()
    
    if args.stats:
        stats = service.get_file_statistics(args.input_file)
        if stats['success']:
            print("\n📊 File Statistics:")
            print(f"  Points: {stats['point_count']}")
            print(f"  Bounds X: {stats['bounds']['min_x']:.2f} to {stats['bounds']['max_x']:.2f}")
            print(f"  Bounds Y: {stats['bounds']['min_y']:.2f} to {stats['bounds']['max_y']:.2f}")
            print(f"  Bounds Z: {stats['bounds']['min_z']:.2f} to {stats['bounds']['max_z']:.2f}")
            print(f"  Mean spacing: {stats['spacing']['mean_spacing']:.2f} m")
            print(f"  Min spacing: {stats['spacing']['min_spacing']:.2f} m")
            print(f"  Max spacing: {stats['spacing']['max_spacing']:.2f} m")
        else:
            print(f"Error: {stats['error']}", file=sys.stderr)
            return 1
        return 0
    
    interp_method = InterpolationMethod.LINEAR
    if args.interpolation == 'cubic':
        interp_method = InterpolationMethod.CUBIC
    elif args.interpolation == 'nearest':
        interp_method = InterpolationMethod.NEAREST
    
    densification_settings = DensificationSettings(
        enabled=args.densify,
        grid_spacing=args.grid_spacing,
        interpolation_method=interp_method,
        show_generated_layer=args.show_generated,
        show_triangles_layer=args.show_triangles,
        max_points=args.max_points,
        min_spacing_threshold=args.min_spacing
    )
    
    settings = ProjectSettings(
        scale=1.0,
        densification=densification_settings
    )
    
    if args.densify:
        print("\n🔧 Densification Settings:")
        print(DensificationConversation.get_summary(densification_settings))
    
    print(f"\n⚙️ Processing {args.input_file}...")
    
    results = service.process_project(args.input_file, args.output_file, settings)
    
    if results['success']:
        print("\n✅ Processing completed successfully!")
        print(f"\n📊 Results:")
        print(f"  Points loaded: {results['points_loaded']}")
        print(f"  Original triangles: {results['original_triangles']}")
        print(f"  TIN quality: {results['tin_quality']:.3f}")
        
        if 'densification' in results:
            print(f"\n{DensificationConversation.get_processing_message(results['densification'])}")
        
        print(f"\n📁 Output saved to: {results['output_path']}")
        return 0
    else:
        print(f"\n❌ Processing failed: {results.get('error', 'Unknown error')}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
