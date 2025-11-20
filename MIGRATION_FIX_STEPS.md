# 🔧 Migration Fix - Step by Step Guide

## Current Status: ✅ Migration files cleaned successfully!

Your migrations directory now only has:
- `0001_initial.py` (original migration)
- `__init__.py` (required file)

## 🚀 Next Steps (Run these in order):

### Step 1: Create new migration for enhanced models
```powershell
python manage.py makemigrations drowsiness_app
```

### Step 2: Apply the migration
```powershell
# If this is a fresh database:
python manage.py migrate

# If you have existing data and get conflicts:
python manage.py migrate --fake-initial
```

### Step 3: Test the system
```powershell
python manage.py runserver
```

## 🎯 What to Expect:

### Step 1 Results:
- Should create a new migration file (like `0002_auto_xxx.py`)
- Will detect the new fields added to your models
- Should say "Adding field..." for each new enhancement

### Step 2 Results:
- Should apply changes to your database
- Adds new columns to existing tables
- Creates the new `MonitoringSession` table

### Step 3 Results:
- Server should start without errors
- You can access the dashboard
- New architecture is ready to use

## 🚨 If You Get Errors:

### Error: "Column already exists"
```powershell
python manage.py migrate --fake-initial
```

### Error: "Table doesn't exist"
```powershell
python manage.py migrate --run-syncdb
```

### Error: "Migration conflicts"
```powershell
# Delete the new migration and try again
rm drowsiness_app/migrations/0002_*.py
python manage.py makemigrations drowsiness_app --empty
# Then manually edit the migration file
```

## ✅ Success Indicators:

After Step 1:
- New migration file created in `drowsiness_app/migrations/`
- No error messages about missing dependencies

After Step 2:
- Database tables updated successfully
- No foreign key constraint errors

After Step 3:
- Django server starts on http://127.0.0.1:8000
- Can access login/register pages
- Dashboard loads (after login)

## 🎉 What You'll Have After Success:

1. **Enhanced Models** with new fields:
   - `Alert` model: severity, confidence, status
   - `UserSettings` model: detection_mode, camera_index
   - `DriverProfile` model: verification fields
   - New `MonitoringSession` model

2. **Clean Architecture**:
   - Service layer for business logic
   - Repository pattern for data access
   - Proper error handling

3. **Better Configuration**:
   - Environment-based settings
   - Configurable detection parameters

## 🏃‍♂️ Ready to Continue?

Run Step 1 now:
```powershell
python manage.py makemigrations drowsiness_app
```

Then come back and let me know if it works or if you get any errors!