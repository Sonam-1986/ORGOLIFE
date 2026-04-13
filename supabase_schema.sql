-- ── Idempotent Type Creation ──────────────────────────────────────
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'user_role') THEN
        CREATE TYPE user_role AS ENUM ('user', 'donor', 'receiver', 'hospital_admin');
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'user_status') THEN
        CREATE TYPE user_status AS ENUM ('active', 'inactive', 'suspended');
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'donor_status') THEN
        CREATE TYPE donor_status AS ENUM ('pending', 'approved', 'rejected');
    END IF;
END $$;

-- ── Table: Users ────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role user_role NOT NULL DEFAULT 'user',
    contact_number TEXT,
    status user_status NOT NULL DEFAULT 'active',
    is_verified_email BOOLEAN DEFAULT false,
    hospital_id UUID REFERENCES public.hospitals(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- ── Table: Donors ───────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.donors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID UNIQUE REFERENCES public.users(id) ON DELETE CASCADE,
    age INTEGER,
    father_name TEXT,
    state TEXT,
    city TEXT,
    full_address TEXT,
    aadhaar_card_path TEXT,
    pan_card_path TEXT,
    medical_report_path TEXT,
    aadhaar_number TEXT,
    pan_number TEXT,
    verified BOOLEAN DEFAULT false,
    status donor_status DEFAULT 'pending',
    verified_by_hospital TEXT,
    verified_by_admin_id UUID REFERENCES public.users(id) ON DELETE SET NULL,
    rejection_reason TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- ── Table: Receivers ────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.receivers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID UNIQUE REFERENCES public.users(id) ON DELETE CASCADE,
    age INTEGER,
    father_name TEXT,
    state TEXT,
    city TEXT,
    aadhaar_card_path TEXT,
    pan_card_path TEXT,
    medical_report_path TEXT,
    aadhaar_number TEXT,
    pan_number TEXT,
    status donor_status DEFAULT 'pending',
    verified_by_hospital TEXT,
    verified_by_admin_id UUID REFERENCES public.users(id) ON DELETE SET NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- ── Table: Hospitals ────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.hospitals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    admin_user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    state TEXT,
    city TEXT,
    address TEXT,
    contact_number TEXT,
    registration_number TEXT UNIQUE NOT NULL,
    specializations TEXT[] DEFAULT '{}',
    aadhaar_path TEXT,
    pan_path TEXT,
    cert_path TEXT,
    is_active BOOLEAN DEFAULT true,
    total_approvals INTEGER DEFAULT 0,
    total_rejections INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- ── Table: Organ Registrations ──────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.organ_registrations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    donor_id UUID REFERENCES public.donors(id) ON DELETE CASCADE,
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    organ_name TEXT NOT NULL,
    blood_group TEXT NOT NULL,
    health_report TEXT,
    hospitals_selected TEXT[],
    state TEXT,
    city TEXT,
    is_available BOOLEAN DEFAULT true,
    matched_receiver_id UUID REFERENCES public.receivers(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- ── Indexes (Idempotent) ───────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_organ_search ON public.organ_registrations (organ_name, blood_group);
CREATE INDEX IF NOT EXISTS idx_organ_location ON public.organ_registrations (state, city);
CREATE INDEX IF NOT EXISTS idx_users_role ON public.users (role);
CREATE INDEX IF NOT EXISTS idx_donors_status ON public.donors (status);
CREATE INDEX IF NOT EXISTS idx_donors_verified ON public.donors (verified);

-- ══════════════════════════════════════════════════════════════════
-- ⚠️  IMPORTANT: RUN THIS IN SUPABASE SQL EDITOR IF TABLES ALREADY EXIST
--    This fixes any missing columns in the receivers table.
-- ══════════════════════════════════════════════════════════════════

ALTER TABLE public.receivers
    ADD COLUMN IF NOT EXISTS status donor_status DEFAULT 'pending',
    ADD COLUMN IF NOT EXISTS verified_by_hospital TEXT,
    ADD COLUMN IF NOT EXISTS verified_by_admin_id UUID REFERENCES public.users(id) ON DELETE SET NULL,
    ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT true;

-- Fix donors table if any columns are missing
ALTER TABLE public.donors
    ADD COLUMN IF NOT EXISTS verified BOOLEAN DEFAULT false,
    ADD COLUMN IF NOT EXISTS status donor_status DEFAULT 'pending',
    ADD COLUMN IF NOT EXISTS verified_by_hospital TEXT,
    ADD COLUMN IF NOT EXISTS verified_by_admin_id UUID REFERENCES public.users(id) ON DELETE SET NULL,
    ADD COLUMN IF NOT EXISTS rejection_reason TEXT;
