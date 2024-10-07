from utils import (
    convert_meters_to_pixel_distance, 
    convert_pixel_distance_to_meters, 
    get_foot_position, 
    get_closest_keypoint_index,
    get_height_of_bbox,
    measure_xy_distance,
    get_center_of_bbox,
    measure_distance
    )
import cv2
from constans import (
    DOUBLE_LINE_WIDTH, 
    NO_MANS_LAND_HEIGHT, 
    DOUBLE_ALLY_DIFFERENCE, 
    SINGLE_LINE_WIDTH,
    PLAYER_1_HEIGHT_METERS,
    PLAYER_2_HEIGHT_METERS
    )
import sys
import numpy as np

sys.path.append('../')


class MiniCourt:
    def __init__(self, frame):
        self.drawing_rectangle_width = 250
        self.drawing_rectangle_height = 450
        self.buffer = 50
        self.padding_court = 20

        self.set_canvas_background_box_position(frame)
        self.set_mini_court_position()
        self.set_court_drawing_key_points()
        self.set_court_lines()

    def set_canvas_background_box_position(self, frame):
        frame = frame.copy()
        self.start_x = frame.shape[1] - self.buffer - self.drawing_rectangle_width
        self.start_y = self.buffer
        self.end_x = frame.shape[1] - self.buffer
        self.end_y = self.buffer + self.drawing_rectangle_height

    def set_mini_court_position(self):
        self.court_start_x = self.start_x + self.padding_court
        self.court_start_y = self.start_y + self.padding_court
        self.court_end_x = self.end_x - self.padding_court
        self.court_end_y = self.end_y - self.padding_court
        self.court_drawing_width = self.court_end_x - self.court_start_x

    def convert_meters_to_pixels(self, meters):
        return convert_meters_to_pixel_distance(meters,
                                                DOUBLE_LINE_WIDTH,
                                                self.court_drawing_width
                                                )

    def set_court_drawing_key_points(self):
        drawing_key_points = [0] * 28
        # point 0
        drawing_key_points[0], drawing_key_points[1] = int(self.court_start_x), int(self.court_start_y)
        # point 1
        drawing_key_points[2], drawing_key_points[3] = int(self.court_end_x), int(self.court_start_y)
        # point 2
        drawing_key_points[4], drawing_key_points[5] = int(self.court_start_x), int(self.court_end_y)
        # point 3
        drawing_key_points[6], drawing_key_points[7] = int(self.court_end_x), int(self.court_end_y)
        # point 4
        drawing_key_points[8] = drawing_key_points[0] + self.convert_meters_to_pixels(DOUBLE_ALLY_DIFFERENCE)
        drawing_key_points[9] = drawing_key_points[1]
        # #point 5
        drawing_key_points[10] = drawing_key_points[4] + self.convert_meters_to_pixels(DOUBLE_ALLY_DIFFERENCE)
        drawing_key_points[11] = drawing_key_points[5]
        # #point 6
        drawing_key_points[12] = drawing_key_points[2] - self.convert_meters_to_pixels(DOUBLE_ALLY_DIFFERENCE)
        drawing_key_points[13] = drawing_key_points[3]
        # #point 7
        drawing_key_points[14] = drawing_key_points[6] - self.convert_meters_to_pixels(DOUBLE_ALLY_DIFFERENCE)
        drawing_key_points[15] = drawing_key_points[7]
        # #point 8
        drawing_key_points[16] = drawing_key_points[8]
        drawing_key_points[17] = drawing_key_points[9] + self.convert_meters_to_pixels(NO_MANS_LAND_HEIGHT)
        # # #point 9
        drawing_key_points[18] = drawing_key_points[16] + self.convert_meters_to_pixels(SINGLE_LINE_WIDTH)
        drawing_key_points[19] = drawing_key_points[17]
        # #point 10
        drawing_key_points[20] = drawing_key_points[10]
        drawing_key_points[21] = drawing_key_points[11] - self.convert_meters_to_pixels(NO_MANS_LAND_HEIGHT)
        # # #point 11
        drawing_key_points[22] = drawing_key_points[20] + self.convert_meters_to_pixels(SINGLE_LINE_WIDTH)
        drawing_key_points[23] = drawing_key_points[21]
        # # #point 12
        drawing_key_points[24] = int((drawing_key_points[16] + drawing_key_points[18]) / 2)
        drawing_key_points[25] = drawing_key_points[17]
        # # #point 13
        drawing_key_points[26] = int((drawing_key_points[20] + drawing_key_points[22]) / 2)
        drawing_key_points[27] = drawing_key_points[21]

        self.drawing_key_points = drawing_key_points

    def set_court_lines(self):
        self.lines = [
            (0, 2),
            (4, 5),
            (6, 7),
            (1, 3),

            (0, 1),
            (8, 9),
            (10, 11),
            (10, 11),
            (2, 3)
        ]

    def draw_background_rectangle(self, frame):
        shapes = np.zeros_like(frame, np.uint8)

        cv2.rectangle(shapes, (self.start_x, self.start_y), (self.end_x, self.end_y), (255, 255, 255), cv2.FILLED)
        out = frame.copy()
        mask = (shapes != 0)
        out[mask] = cv2.addWeighted(frame, 0.5, shapes, 0.5, 0)[mask]

        return out

    def draw_court(self, frame):
        for i in range(0, len(self.drawing_key_points), 2):
            x = int(self.drawing_key_points[i])
            y = int(self.drawing_key_points[i + 1])
            cv2.circle(frame, (x, y), 5, (0, 0, 255), -1)

        for line in self.lines:
            start_point = (int(self.drawing_key_points[line[0] * 2]), int(self.drawing_key_points[line[0] * 2 + 1]))
            end_point = (int(self.drawing_key_points[line[1] * 2]), int(self.drawing_key_points[line[1] * 2 + 1]))
            cv2.line(frame, start_point, end_point, (0, 0, 0), 2)

        net_start_point = (int(self.drawing_key_points[0]),
                           int((self.drawing_key_points[1] + self.drawing_key_points[5]) / 2))
        net_end_point = (int(self.drawing_key_points[2]),
                         int((self.drawing_key_points[1] + self.drawing_key_points[5]) / 2))
        cv2.line(frame, net_start_point, net_end_point, (255, 0, 0), 2)

        return frame

    def get_start_point_of_mini_court(self):
        return self.court_start_x, self.court_start_y

    def get_width_of_mini_court(self):
        return self.court_drawing_width

    def get_court_drawing_keypoints(self):
        return self.drawing_key_points

    def draw_mini_court(self, frames):
        output_frames = []
        for frame in frames:
            frame = self.draw_background_rectangle(frame)
            frame = self.draw_court(frame)
            output_frames.append(frame)

        return output_frames
    
    def get_mini_court_coordinates(self, 
                                   object_position,
                                   closest_keypoint,
                                   closest_keypoint_index,
                                   player_height_in_pixels,
                                   player_height_in_meters
                                   ):
        
        distance_from_keypoint_x_pixels, distance_from_keypoint_y_pixels = measure_xy_distance(
            object_position, closest_keypoint
        )
        
        distance_from_keypoint_x_meters = convert_pixel_distance_to_meters(
                                                                            distance_from_keypoint_x_pixels, 
                                                                            player_height_in_meters, 
                                                                            player_height_in_pixels
                                                                           )
        
        distance_from_keypoint_y_meters = convert_pixel_distance_to_meters(
            distance_from_keypoint_y_pixels, player_height_in_meters, player_height_in_pixels
        )
        
        # convert to mini court co-ordinates
        mini_court_x_distance_pixels  = self.convert_meters_to_pixels(distance_from_keypoint_x_meters)
        mini_court_y_distance_pixels = self.convert_meters_to_pixels(distance_from_keypoint_y_meters)
        closest_mini_court_keypoint = (
            self.drawing_key_points[closest_keypoint_index*2],
            self.drawing_key_points[closest_keypoint_index*2 + 1]
        )
        
        mini_court_player_position = (
            closest_mini_court_keypoint[0] + mini_court_x_distance_pixels,
            closest_mini_court_keypoint[1] + mini_court_y_distance_pixels
        )
        
        return mini_court_player_position
    
    def convert_bounding_boxes_to_mini_court_coordinates(self, player_boxes, ball_boxes, original_court_keypoints):
        
        player_heights = {
            1: PLAYER_1_HEIGHT_METERS,
            2: PLAYER_2_HEIGHT_METERS
        }
        
        output_player_boxes = []
        output_ball_boxes = []
        
        for frame_num, player_bbox in enumerate(player_boxes):
            ball_box = ball_boxes[frame_num][1]
            ball_position = get_center_of_bbox(ball_box)
            closest_player_id_to_ball = min(player_bbox.keys(), key = lambda x: measure_distance(
                ball_position, get_center_of_bbox(player_bbox[x])
            ))
            
            output_player_bbox_dict = {}
            
            for player_id, bbox in player_bbox.items():
                
                foot_position = get_foot_position(bbox)
                
                closest_keypoint_index = get_closest_keypoint_index(
                    foot_position, original_court_keypoints, [0, 2, 12, 13]
                )
                
                closest_key_point = (
                    original_court_keypoints[2 * closest_keypoint_index],
                    original_court_keypoints[2 * closest_keypoint_index + 1]
                )
                
                frame_index_min = max(0, frame_num - 20)
                frame_index_max = min(len(player_boxes), frame_num + 50)
                bboxes_height_in_pixels = [get_height_of_bbox(player_boxes[i][player_id]) for i in range(
                    frame_index_min, frame_index_max
                )]
                
                max_player_height_in_pixels = max(bboxes_height_in_pixels)
                
                mini_court_player_position = self.get_mini_court_coordinates(
                    foot_position,
                    closest_key_point,
                    closest_keypoint_index,
                    max_player_height_in_pixels,
                    player_heights[player_id]
                )
                
                output_player_bbox_dict[player_id] = mini_court_player_position
                
                if closest_player_id_to_ball == player_id:
                    
                    closest_keypoint_index = get_closest_keypoint_index(ball_position, original_court_keypoints, [0, 2, 12, 13])
                    
                    closest_key_point = (
                        original_court_keypoints[closest_keypoint_index*2],
                        original_court_keypoints[closest_keypoint_index*2 + 1]
                    )
                    
                    mini_court_ball_position = self.get_mini_court_coordinates(
                        ball_position,
                        closest_key_point,
                        closest_keypoint_index,
                        max_player_height_in_pixels,
                        player_heights[player_id]
                    )
                    
                    output_ball_boxes.append({1: mini_court_ball_position})
            
            output_player_boxes.append(output_player_bbox_dict)
            
        return output_player_boxes, output_ball_boxes
    
    def draw_points_on_mini_court(self, frames, positions, color=(0, 255, 0)):
        for frame_num, frame in enumerate(frames):
            for _ , position in positions[frame_num].items():
                x, y = position
                x = int(x)
                y = int(y)
                cv2.circle(frame, (x,y), 5, color, -1)
        
        return frames