"""Demo script for testing bot functionality locally."""

import asyncio
from pathlib import Path
from src.bot.file_parser import FileParser
from src.models.bot_data import ColumnMapping, BotSessionData


async def demo_file_parsing():
    """Demonstrate file parsing functionality."""
    print("=" * 60)
    print("Bot Workflow Demo - File Parsing")
    print("=" * 60)
    
    # Use sample file
    sample_file = Path(__file__).parent / "sample_survey_data.txt"
    
    if not sample_file.exists():
        print(f"❌ Sample file not found: {sample_file}")
        return
    
    print(f"\n📄 Processing file: {sample_file.name}")
    
    # Step 1: Validate file
    print("\n1️⃣ Validating file...")
    is_valid, error = FileParser.validate_file(sample_file)
    if not is_valid:
        print(f"   ❌ Validation failed: {error}")
        return
    print("   ✅ File is valid")
    
    # Step 2: Detect encoding
    print("\n2️⃣ Detecting encoding...")
    encoding = FileParser.detect_encoding(sample_file)
    print(f"   📝 Detected encoding: {encoding}")
    
    # Step 3: Detect delimiter
    print("\n3️⃣ Detecting delimiter...")
    delimiter = FileParser.detect_delimiter(sample_file, encoding)
    delimiter_name = {
        ' ': 'space',
        '\t': 'tab',
        ',': 'comma',
        ';': 'semicolon'
    }.get(delimiter, repr(delimiter))
    print(f"   📝 Detected delimiter: {delimiter_name}")
    
    # Step 4: Parse file
    print("\n4️⃣ Parsing file...")
    column_mapping = ColumnMapping(
        x_col=0,
        y_col=1,
        z_col=2,
        code_col=3,
        comment_col=4
    )
    
    parsed_data = FileParser.parse_file(
        sample_file,
        encoding,
        delimiter,
        column_mapping
    )
    
    print(f"   📊 Total rows: {parsed_data.total_rows}")
    print(f"   ✅ Valid points: {parsed_data.valid_rows}")
    print(f"   ❌ Invalid rows: {parsed_data.invalid_rows}")
    
    if parsed_data.warnings:
        print(f"   ⚠️  Warnings: {len(parsed_data.warnings)}")
        for warning in parsed_data.warnings[:3]:
            print(f"      • {warning}")
    
    if parsed_data.anomalies:
        print(f"   ⚠️  Anomalies: {len(parsed_data.anomalies)}")
        for anomaly in parsed_data.anomalies[:3]:
            print(f"      • {anomaly}")
    
    # Step 5: Show sample points
    print("\n5️⃣ Sample parsed points:")
    for i, point in enumerate(parsed_data.points[:5], 1):
        code = point.get('code', '—')
        comment = point.get('comment', '—')
        print(f"   {i}. X={point['x']:.2f}, Y={point['y']:.2f}, Z={point['z']:.2f}, "
              f"Code={code}, Comment={comment[:30]}...")
    
    # Step 6: Simulate session data
    print("\n6️⃣ Simulating bot session...")
    session = BotSessionData()
    from src.models.bot_data import FileUploadInfo
    
    session.file_info = FileUploadInfo(
        file_path=sample_file,
        original_filename=sample_file.name,
        file_size=sample_file.stat().st_size,
        encoding=encoding,
        delimiter=delimiter
    )
    session.parsed_data = parsed_data
    session.scale = 1000.0
    session.tin_enabled = True
    session.densification_enabled = True
    session.use_template = False
    
    print(f"   📦 Session initialized:")
    print(f"      • File: {session.file_info.original_filename}")
    print(f"      • Points: {session.parsed_data.valid_rows}")
    print(f"      • Scale: 1:{int(session.scale)}")
    print(f"      • TIN: {'✅ Enabled' if session.tin_enabled else '⏭️ Disabled'}")
    print(f"      • Densification: {'✅ Enabled' if session.densification_enabled else '⏭️ Disabled'}")
    print(f"      • Template: {'✅ Yes' if session.use_template else '⏭️ No'}")
    
    print("\n" + "=" * 60)
    print("✅ Demo completed successfully!")
    print("=" * 60)
    print("\nTo start the actual bot:")
    print("  1. Set TELEGRAM_BOT_TOKEN environment variable")
    print("  2. Run: python bot_main.py")
    print()


if __name__ == "__main__":
    asyncio.run(demo_file_parsing())
