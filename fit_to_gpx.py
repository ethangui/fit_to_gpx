import sys
from fitparse import FitFile
import gpxpy
import gpxpy.gpx
from datetime import datetime, timezone

def fit_to_gpx(fit_path, gpx_path):
    fitfile = FitFile(fit_path)
    
    # Extract activity information if available
    activity_name = None
    activity_type = None
    for record in fitfile.get_messages('session'):
        for data in record:
            if data.name == 'sport' and data.value is not None:
                activity_type = data.value
            if data.name == 'start_time' and data.value is not None:
                activity_name = f"Activity {data.value.strftime('%Y-%m-%d %H:%M:%S')}"

    # Create GPX
    gpx = gpxpy.gpx.GPX()
    
    # Add metadata
    gpx.creator = "fit_to_gpx.py"
    if activity_name:
        gpx.name = activity_name
    
    gpx_track = gpxpy.gpx.GPXTrack()
    gpx.tracks.append(gpx_track)
    
    # Set track name and type if available
    if activity_name:
        gpx_track.name = activity_name
    if activity_type:
        gpx_track.type = str(activity_type)
    
    # Extract lap information
    laps = []
    for lap_msg in fitfile.get_messages('lap'):
        lap_data = {}
        for data in lap_msg:
            lap_data[data.name] = data.value
        laps.append(lap_data)
    
    # If no laps found, create a single segment for all points
    if not laps:
        gpx_segment = gpxpy.gpx.GPXTrackSegment()
        gpx_track.segments.append(gpx_segment)
        segments = [gpx_segment]
    else:
        # Create a segment for each lap
        segments = []
        for lap in laps:
            gpx_segment = gpxpy.gpx.GPXTrackSegment()
            gpx_track.segments.append(gpx_segment)
            segments.append(gpx_segment)
    
    # Process all points
    current_lap = 0
    lap_start_times = [lap.get('start_time', datetime.now(timezone.utc)) for lap in laps] if laps else [datetime.now(timezone.utc)]
    
    for record in fitfile.get_messages('record'):
        data = {}
        for d in record:
            data[d.name] = d.value

        if 'position_lat' in data and 'position_long' in data and data['position_lat'] is not None and data['position_long'] is not None:
            lat = data['position_lat'] * (180 / 2**31)
            lon = data['position_long'] * (180 / 2**31)
            elevation = data.get('altitude', None)
            timestamp = data.get('timestamp', datetime.now(timezone.utc))
            
            # Determine which lap/segment this point belongs to
            if laps:
                while current_lap < len(lap_start_times) - 1 and timestamp >= lap_start_times[current_lap + 1]:
                    current_lap += 1
            
            point = gpxpy.gpx.GPXTrackPoint(
                latitude=lat, 
                longitude=lon, 
                elevation=elevation, 
                time=timestamp
            )
            
            # Add speed if available (standard GPX field)
            if 'speed' in data and data['speed'] is not None:
                point.speed = data['speed']
            
            # Add point to the appropriate segment
            segments[current_lap].points.append(point)

    with open(gpx_path, 'w') as f:
        f.write(gpx.to_xml())
    print(f"GPX file saved to {gpx_path}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python fit_to_gpx.py input.fit output.gpx")
    else:
        fit_to_gpx(sys.argv[1], sys.argv[2])