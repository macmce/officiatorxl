# Generated manually on 2025-06-09
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('officials', '0022_alter_position_unique_together_and_more'),
    ]

    operations = [
        # SQL to explicitly create the unique constraint for PostgreSQL
        migrations.RunSQL(
            # Forward SQL
            """
            -- Drop any existing unique constraints on officials_position table
            DO $$ 
            DECLARE
                constraint_name text;
            BEGIN
                FOR constraint_name IN (
                    SELECT conname FROM pg_constraint 
                    WHERE conrelid = 'officials_position'::regclass 
                    AND contype = 'u'
                )
                LOOP
                    EXECUTE 'ALTER TABLE officials_position DROP CONSTRAINT IF EXISTS ' || constraint_name;
                END LOOP;
            END $$;
            
            -- Create the new unique constraint with all three fields
            ALTER TABLE officials_position 
            ADD CONSTRAINT officials_position_role_strategy_id_location_unq 
            UNIQUE (role, strategy_id, location);
            """,
            
            # Reverse SQL
            """
            -- Drop new constraint
            ALTER TABLE officials_position DROP CONSTRAINT IF EXISTS officials_position_role_strategy_id_location_unq;
            
            -- Add back old constraint
            ALTER TABLE officials_position ADD CONSTRAINT officials_position_role_strategy_id_key UNIQUE (role, strategy_id);
            """
        ),
    ]
