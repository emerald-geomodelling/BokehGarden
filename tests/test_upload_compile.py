# test_upload_compile.py - Run this to test TypeScript compilation
import sys
import os

# Add bokeh_garden to path
sys.path.insert(0, os.path.abspath('..'))

print("=" * 60)
print("Testing Upload TypeScript Compilation")
print("=" * 60)

try:
	from bokeh_garden.upload import Upload

	print("[✓] Upload class imported successfully")

	# Check if __implementation__ exists
	if hasattr(Upload, '__implementation__'):
		print("[✓] __implementation__ attribute exists")
		impl = Upload.__implementation__
		print(f"[✓] Implementation type: {type(impl)}")

		# Try to access the compiled code
		if hasattr(impl, 'code'):
			print(f"[✓] Compiled code length: {len(impl.code)} characters")
			print("\n[COMPILED CODE PREVIEW]")
			print(impl.code[:500])
			print("...\n")
		else:
			print("[!] No 'code' attribute on implementation")
			print(f"[DEBUG] Implementation attributes: {dir(impl)}")
	else:
		print("[✗] No __implementation__ attribute!")

	# Try to create an instance
	print("\n[TEST] Creating Upload instance...")
	upload = Upload(accept=".csv,.txt")
	print(f"[✓] Upload instance created: {upload}")
	print(f"[✓] Upload ID: {upload.upload_id}")
	print(f"[✓] Upload URL: {upload.upload_url}")
	print(f"[✓] Accept: {upload.accept}")

	print("\n[SUCCESS] All checks passed!")

except Exception as e:
	print(f"\n[✗ ERROR] {e}")
	import traceback

	traceback.print_exc()
