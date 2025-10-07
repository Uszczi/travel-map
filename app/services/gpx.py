import gpxpy
import gpxpy.gpx


class GPXService:
    # TODO refactor this after adding injector
    @classmethod
    def points_to_gpx(
        cls, points: list[tuple[float, float]], track_name: str
    ) -> gpxpy.gpx.GPX:
        """Generuje GPX z listy punktów."""
        gpx = gpxpy.gpx.GPX()

        gpx_track = gpxpy.gpx.GPXTrack(name=track_name)
        gpx.tracks.append(gpx_track)
        gpx_segment = gpxpy.gpx.GPXTrackSegment()
        gpx_track.segments.append(gpx_segment)

        for p in points:
            lat, lon = p[0], p[1]
            ele = p[2] if len(p) > 2 else None
            gpx_segment.points.append(
                gpxpy.gpx.GPXTrackPoint(lat, lon, elevation=ele, time=None)
            )

        return gpx
