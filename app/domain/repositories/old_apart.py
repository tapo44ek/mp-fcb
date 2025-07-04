from sqlalchemy.orm import sessionmaker
from sqlalchemy import Select, text
from domain.entities.old_apart import OldApart

class OldApartRepository: 
    def __init__(self, engine : sessionmaker):
        self.create_session = engine

    async def create_old_apart(self, affair_id, fio, house_address, apart_number, problems):
        pass
        
    async def get_old_apart(self): 
        async with self.create_session() as session: 
            result = await session.execute(text('''
            SELECT jsonb_object_agg(
                o.affair_id,
                jsonb_build_object(
                    'fio', o.fio,
                    'house_address', o.house_address,
                    'apart_number', o.apart_number,
                    'status', s.status,
                    'problems', o.problems,
					'affair_id', affair_id
                )
            ) AS combined_json
            FROM 
                mprg.old_apart o
            JOIN 
                mprg.status s ON o.status_id = s.status_id;'''))
            
            row = result.fetchone()
            return row[0] if row else {}
        
    async def get_stage_history(self, affair_id : int): 
        async with self.create_session() as session: 
            result = await session.execute(text("""
            WITH stage_info AS (
            SELECT 
                o.affair_id,
                p.problem_id,
                jsonb_build_object(
                    'stage_id', sh.stage_id,
                    'stage', s.stage,
                    'doc_date', sh.doc_date,
                    'document_number', sh.document_number,
                    'created_at', sh.created_at,
                    'updated_at', sh.updated_at,
                    'stage_status', ss.stage_status,
					'next_stages', s.next_stage
                ) AS stage_json,
                sh.created_at
                FROM 
                    mprg.stage_history sh
                JOIN mprg.stage s USING (stage_id)
                JOIN mprg.old_apart o USING (affair_id)
                JOIN mprg.problems p USING (problem_id)
                JOIN mprg.stage_status ss USING (stage_status_id)
                WHERE affair_id = :affair_id
            )
            SELECT 
                affair_id,
                jsonb_object_agg(
                    problem_id::text,
                    (
                        SELECT jsonb_agg(si.stage_json ORDER BY si.created_at)
                        FROM stage_info si
                        WHERE si.affair_id = stage_info.affair_id 
                        AND si.problem_id = stage_info.problem_id
                    )
                ) AS problem_stages
            FROM 
                stage_info
            GROUP BY 
                affair_id
            ORDER BY 
                affair_id;
            """
            ), {'affair_id' : affair_id})
            row = result.fetchone()
            return {
            "affair_id": row[0],
            "problem_stages": row[1]
            }

