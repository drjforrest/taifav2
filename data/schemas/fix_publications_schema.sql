-- Migration: Fix publications table schema
-- Date: 2025-08-09
-- Description: Adds missing authors column and ensures schema consistency

-- Add the authors column as a text array if it doesn't exist
DO $$ 
BEGIN
    -- Check if authors column exists
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'publications' AND column_name = 'authors'
    ) THEN
        -- Add the authors column
        ALTER TABLE publications ADD COLUMN authors text[];
        
        -- Create an index for better performance when searching authors
        CREATE INDEX IF NOT EXISTS idx_publications_authors ON publications USING gin(authors);
        
        RAISE NOTICE 'Added authors column to publications table';
    ELSE
        RAISE NOTICE 'Authors column already exists in publications table';
    END IF;
END $$;

-- Verify the column was added successfully
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'publications' 
  AND column_name IN ('authors', 'title', 'abstract', 'publication_date', 'source');

-- Success message
SELECT 'Publications table schema fix completed successfully!' as result;
