
import pandas as pd
from pathlib import Path
import json
import glob
from exploring_json_data_struct import extract_match_data
from database_model import DatabaseManager, CricketDelivery, CricketMatch, get_database_config

PROJECT_ROOT = Path(__file__).parent.parent
CODE_DIR = PROJECT_ROOT / 'code'
DATA_DIR = PROJECT_ROOT / 'data'

class NepalODIProcessor:
    def __init__(self, database_url=None):
        self.data_dir = DATA_DIR / "Nepal" / "ODI"
        self.database_url = database_url or get_database_config()
        self.db_manager = DatabaseManager(self.database_url)
        
    def get_all_odi_files(self):
        """Get all JSON files in Nepal/ODI directory"""
        json_files = list(self.data_dir.glob("*.json"))
        print(f"Found {len(json_files)} ODI match files")
        return json_files
    
    def extract_match_id(self, file_path):
        """Extract match ID from filename"""
        return file_path.stem  # Gets filename without extension
    
    def process_match_info(self, match_data, match_id):
        """Extract and return match information"""
        try:
            info = match_data.data['info']
            
            # Extract team names
            teams = info.get('teams', [])
            team1 = teams[0] if len(teams) > 0 else None
            team2 = teams[1] if len(teams) > 1 else None
            
            # Extract toss info
            toss = info.get('toss', {})
            toss_winner = toss.get('winner')
            toss_decision = toss.get('decision')
            
            # Extract outcome
            outcome = info.get('outcome', {})
            winner = outcome.get('winner')
            result = outcome.get('result')
            
            # Extract venue info
            venue = info.get('venue')
            city = info.get('city')
            
            # Extract dates
            dates = info.get('dates', [])
            match_date = dates[0] if dates else None
            
            # Extract player of match
            player_of_match = None
            if 'player_of_match' in info:
                pom = info['player_of_match']
                player_of_match = pom[0] if isinstance(pom, list) and pom else pom
            
            match_info = CricketMatch(
                match_id=match_id,
                match_type=info.get('match_type'),
                match_type_number=info.get('match_type_number'),
                gender=info.get('gender'),
                venue=venue,
                city=city,
                dates=str(match_date),
                team1=team1,
                team2=team2,
                toss_winner=toss_winner,
                toss_decision=toss_decision,
                winner=winner,
                result_type=result,
                player_of_match=player_of_match
            )
            
            return match_info
            
        except Exception as e:
            print(f"Error processing match info for {match_id}: {e}")
            return None
    
    def process_deliveries(self, match_data, match_id):
        """Process all deliveries for both innings"""
        all_deliveries = []
        
        try:
            # Process both innings
            for innings_num in range(len(match_data.data['innings'])):
                df = match_data.convert_json_to_df(innings_num)
                
                # Convert DataFrame rows to CricketDelivery objects
                for _, row in df.iterrows():
                    delivery = CricketDelivery(
                        match_id=match_id,
                        innings_number=innings_num,
                        overs=int(row['overs']),
                        balls=int(row['balls']),
                        batter=row['batter'],
                        non_striker=row['non_striker'],
                        bowler=row['bowler'],
                        runs_batter=int(row.get('runs.batter', 0) or 0),
                        runs_extras=int(row.get('runs.extras', 0) or 0),
                        runs_total=int(row.get('runs.total', 0) or 0),
                        extras_wides=int(row['extras.wides']) if pd.notna(row['extras.wides']) else None,
                        extras_legbyes=int(row['extras.legbyes']) if pd.notna(row['extras.legbyes']) else None,
                        extras_noballs=int(row['extras.noballs']) if pd.notna(row['extras.noballs']) else None,
                        description=row.get('description', ''),
                        ball_areas=row.get('ball_areas', ''),
                        is_wicket=int(row.get('is_wicket', 0)),
                        wicket_player_out=row['wicket_player_out'] if pd.notna(row['wicket_player_out']) else None,
                        wicket_kind=row['wicket_kind'] if pd.notna(row['wicket_kind']) else None,
                        wicket_fielder=row['wicket_fielder'] if pd.notna(row['wicket_fielder']) else None,
                        is_drs=row.get('is_drs', ''),
                        is_umpires_call=row.get('is_umpires_call', '')
                    )
                    all_deliveries.append(delivery)
                    
        except Exception as e:
            print(f"Error processing deliveries for {match_id}: {e}")
            
        return all_deliveries
    
    def process_single_match(self, file_path, session):
        """Process a single match file"""
        match_id = self.extract_match_id(file_path)
        print(f"Processing match: {match_id}")
        
        try:
            # Check if match already exists
            existing_match = session.query(CricketMatch).filter_by(match_id=match_id).first()
            if existing_match:
                print(f"  ⏭️  Match {match_id} already exists, skipping...")
                return True
            
            # Load match data
            match_data = extract_match_data(str(file_path))
            
            # Process match info
            match_info = self.process_match_info(match_data, match_id)
            if match_info:
                session.add(match_info)
            
            # Process deliveries
            deliveries = self.process_deliveries(match_data, match_id)
            if deliveries:
                session.add_all(deliveries)
                print(f"  ✅ Added {len(deliveries)} deliveries")
            
            # Commit this match
            session.commit()
            return True
            
        except Exception as e:
            print(f"  ❌ Error processing {match_id}: {e}")
            session.rollback()
            return False
    
    def process_all_matches(self):
        """Process all Nepal ODI matches"""
        # Connect to database
        if not self.db_manager.connect():
            print("Failed to connect to database")
            return False
        
        # Get all files
        json_files = self.get_all_odi_files()
        if not json_files:
            print("No JSON files found")
            return False
        
        session = self.db_manager.get_session()
        successful = 0
        failed = 0
        
        try:
            for file_path in json_files:
                if self.process_single_match(file_path, session):
                    successful += 1
                else:
                    failed += 1
            
            print(f"\n📊 Processing Complete:")
            print(f"✅ Successful: {successful}")
            print(f"❌ Failed: {failed}")
            print(f"📁 Total files: {len(json_files)}")
            
        except Exception as e:
            print(f"Error during batch processing: {e}")
        finally:
            session.close()
            self.db_manager.close()
        
        return successful > 0

def main():
    """Main function to process all Nepal ODI data"""
    print("🏏 Nepal ODI Data Processor")
    print("=" * 40)
    
    # Initialize processor
    processor = NepalODIProcessor()
    
    # Process all matches
    success = processor.process_all_matches()
    
    if success:
        print("\n🎉 Data processing completed successfully!")
    else:
        print("\n💥 Data processing failed!")

if __name__ == "__main__":
    main()
