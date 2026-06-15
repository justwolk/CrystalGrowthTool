from abc import ABC, abstractmethod
import copy
from typing import List

class Command(ABC):
    @abstractmethod
    def execute(self):
        pass
    
    @abstractmethod
    def undo(self):
        pass

class CommandManager:
    def __init__(self, max_history_size: int = 100):
        self._history: List[Command] = []
        self._current_index: int = -1
        self._max_history_size = max_history_size
    
    def execute_command(self, command: Command):
        if self._current_index < len(self._history) - 1:
            self._history = self._history[:self._current_index + 1]
        
        command.execute()
        self._history.append(command)
        self._current_index += 1
        
        if len(self._history) > self._max_history_size:
            self._history.pop(0)
            self._current_index -= 1
    
    def undo(self) -> bool:
        if self._current_index >= 0:
            command = self._history[self._current_index]
            command.undo()
            self._current_index -= 1
            return True
        return False
    
    def redo(self) -> bool:
        if self._current_index < len(self._history) - 1:
            self._current_index += 1
            command = self._history[self._current_index]
            command.execute()
            return True
        return False
    
    def can_undo(self) -> bool:
        return self._current_index >= 0
    
    def can_redo(self) -> bool:
        return self._current_index < len(self._history) - 1

class CrystalCommand(Command):
    def __init__(self, model, update_callback=None):
        self.model = model
        self.update_callback = update_callback
        self.old_state = None
    
    def _save_state(self):
        self.old_state = {
            'crystal_object': copy.deepcopy(self.model.crystal_object),
            'current_image': self.model.current_image,
            'current_layer': self.model.current_layer,
        }
    
    def _restore_state(self, state):
        self.model.crystal_object = copy.deepcopy(state['crystal_object'])
        self.model.current_image = state['current_image']
        self.model.current_layer = state['current_layer']
        if self.update_callback:
            self.update_callback()
    
    def undo(self):
        if self.old_state:
            self._restore_state(self.old_state)

class AddGrowthLinePointCommand(CrystalCommand):
    
    def __init__(self, model, point, update_callback=None):
        super().__init__(model, update_callback)
        self.point = point
    
    def execute(self):
        self._save_state()
        current_image = self.model.current_image
        current_layer = self.model.current_layer
        crystal_object = self.model.crystal_object[current_image]
        
        if not crystal_object.growth_lines:
            crystal_object.growth_lines.append([self.point])
        else:
            if current_layer >= len(crystal_object.growth_lines):
                crystal_object.growth_lines.append([self.point])
            else:
                crystal_object.growth_lines[current_layer].append(self.point)
        
        if self.update_callback:
            self.update_callback()

class DeleteGrowthLinePointCommand(CrystalCommand):
    
    def __init__(self, model, point, update_callback=None):
        super().__init__(model, update_callback)
        self.point = point
    
    def execute(self):
        self._save_state()
        current_image = self.model.current_image
        current_layer = self.model.current_layer
        crystal_object = self.model.crystal_object[current_image]
        
        points = crystal_object.growth_lines[current_layer] if len(crystal_object.growth_lines) > current_layer else []
        if not points:
            return
        
        click_threshold = 100
        closest_point = None
        min_distance = float('inf')
        
        for point in crystal_object.growth_lines[current_layer]:
            distance = (point - self.point).manhattanLength()
            if distance < min_distance:
                min_distance = distance
                closest_point = point
        
        if min_distance <= click_threshold:
            crystal_object.growth_lines[current_layer].remove(closest_point)
        
        if self.update_callback:
            self.update_callback()

class MoveGrowthLinePointCommand(CrystalCommand):
    
    def __init__(self, model, old_point, new_point, update_callback=None):
        super().__init__(model, update_callback)
        self.old_point = old_point
        self.new_point = new_point
    
    def execute(self):
        self._save_state()
        current_image = self.model.current_image
        current_layer = self.model.current_layer
        crystal_object = self.model.crystal_object[current_image]
        
        if not crystal_object.growth_lines or len(crystal_object.growth_lines) <= current_layer:
            return
            
        points = crystal_object.growth_lines[current_layer]
        closest_point = None
        min_distance = float('inf')
        closest_index = None
        
        for i, point in enumerate(points):
            distance = (point - self.old_point).manhattanLength()
            if distance < min_distance:
                min_distance = distance
                closest_point = point
                closest_index = i
        
        if closest_point is not None and closest_index is not None:
            crystal_object.growth_lines[current_layer][closest_index] = self.new_point
        
        if self.update_callback:
            self.update_callback()

class ClearAllPointsCommand(CrystalCommand):
    
    def execute(self):
        self._save_state()
        current_image = self.model.current_image
        crystal_object = self.model.crystal_object[current_image]
        crystal_object.clear_all_points()
        
        if self.update_callback:
            self.update_callback()

class ClearAllPointsEverywhereCommand(CrystalCommand):
    
    def execute(self):
        self._save_state()
        
        for crystal_obj in self.model.crystal_object:
            crystal_obj.clear_all_points()
        
        if self.update_callback:
            self.update_callback()

class DeleteLayerCommand(CrystalCommand):
    
    def execute(self):
        self._save_state()
        current_image = self.model.current_image
        crystal_object = self.model.crystal_object[current_image]
        target_layer = self.model.current_layer
        
        if target_layer >= 0 and target_layer < len(crystal_object.growth_lines):
            del crystal_object.growth_lines[target_layer]
            if self.model.current_layer > target_layer:
                self.model.update_attribute('current_layer', self.model.current_layer - 1)
            elif self.model.current_layer == target_layer:
                new_current_layer = max(len(crystal_object.growth_lines) - 1, 0)
                self.model.update_attribute('current_layer', new_current_layer)
        
        if self.update_callback:
            self.update_callback()

class DeleteLayerPointsCommand(CrystalCommand):
    
    def execute(self):
        self._save_state()
        current_image = self.model.current_image
        crystal_object = self.model.crystal_object[current_image]
        target_layer = self.model.current_layer
        
        if target_layer >= 0 and target_layer < len(crystal_object.growth_lines):
            crystal_object.growth_lines[target_layer] = []
        
        if self.update_callback:
            self.update_callback()

class GenerateIntersectionsCommand(CrystalCommand):
    
    def __init__(self, model, scope, update_callback=None):
        super().__init__(model, update_callback)
        self.scope = scope
        self.grid_lines = None
    
    def set_grid_lines(self, grid_lines):
        self.grid_lines = grid_lines
    
    def execute(self):
        self._save_state()
        
        if self.scope == 'layer':
            self._generate_layer_intersections()
        elif self.scope == 'image':
            self._generate_image_intersections()
        elif self.scope == 'all':
            self._generate_all_intersections()
        
        if self.update_callback:
            self.update_callback()
    
    def _generate_layer_intersections(self):
        from utils.interpolate_curve import cubic_spline_interpolation as interpolate_curve_points
        from utils.line_segments_intersection import find_growth_grid_intersections
        import numpy as np
        from PySide2.QtCore import QPointF

        crystal = self.model.crystal_object[self.model.current_image]
        if self.model.current_layer >= len(crystal.growth_lines):
            return

        crystal.clear_points_for_layer(self.model.current_layer)
        if not self.grid_lines:
            return

        growth_lines = crystal.growth_lines[self.model.current_layer]
        if growth_lines and len(growth_lines) > 1:
            if self.model.interpolation_enabled and len(growth_lines) > 3:
                growth_lines_to_calculate = interpolate_curve_points(growth_lines)
                growth_lines_array = np.array([[point.x(), point.y()] for point in growth_lines_to_calculate])
            else:
                growth_lines_array = np.array([[point.x(), point.y()] for point in growth_lines])
            
            result = find_growth_grid_intersections(growth_lines_array, self.grid_lines)
            
            for intersection, line_idx in result:
                intersection_point = QPointF(intersection[0], intersection[1])
                crystal.set_point(self.model.current_layer, line_idx, intersection_point)
    
    def _generate_image_intersections(self):
        self.model.crystal_object[self.model.current_image].clear_all_points()
        
        current_layer = self.model.current_layer
        growth_lines_count = len(self.model.crystal_object[self.model.current_image].growth_lines)
        for layer in range(growth_lines_count):
            self.model.current_layer = layer
            self._generate_layer_intersections()
        self.model.current_layer = current_layer
    
    def _generate_all_intersections(self):
        image_count = len(self.model.crystal_object)
        current_image = self.model.current_image
        for image_number in range(image_count):
            self.model.current_image = image_number
            self._generate_image_intersections()
        self.model.current_image = current_image

class AddGridLinePointCommand(CrystalCommand):
    
    def __init__(self, model, point, line_index, update_callback=None):
        super().__init__(model, update_callback)
        self.point = point
        self.line_index = line_index
    
    def execute(self):
        self._save_state()
        current_image = self.model.crystal_object[self.model.current_image]
        
        while len(current_image.grid_lines) <= self.line_index:
            current_image.grid_lines.append([])
            
        current_image.grid_lines[self.line_index].append(self.point)
        
        if self.update_callback:
            self.update_callback()

class DeleteGridLinePointCommand(CrystalCommand):
    
    def __init__(self, model, point, line_index, update_callback=None):
        super().__init__(model, update_callback)
        self.point = point
        self.line_index = line_index
    
    def execute(self):
        self._save_state()
        current_image = self.model.crystal_object[self.model.current_image]
        
        if 0 <= self.line_index < len(current_image.grid_lines):
            line = current_image.grid_lines[self.line_index]
            if self.point in line:
                line.remove(self.point)
        
        if self.update_callback:
            self.update_callback()

class MoveGridLinePointCommand(CrystalCommand):
    
    def __init__(self, model, old_point, new_point, line_index, update_callback=None):
        super().__init__(model, update_callback)
        self.old_point = old_point
        self.new_point = new_point
        self.line_index = line_index
    
    def execute(self):
        self._save_state()
        current_image = self.model.crystal_object[self.model.current_image]
        
        if 0 <= self.line_index < len(current_image.grid_lines):
            line = current_image.grid_lines[self.line_index]
            if self.old_point in line:
                index = line.index(self.old_point)
                line[index] = self.new_point
        
        if self.update_callback:
            self.update_callback()


class InsertGrowthLinePointBetweenCommand(CrystalCommand):
    
    def __init__(self, model, point_index1, point_index2, update_callback=None):
        super().__init__(model, update_callback)
        self.point_index1 = point_index1
        self.point_index2 = point_index2
    
    def execute(self):
        self._save_state()
        current_image = self.model.current_image
        current_layer = self.model.current_layer
        crystal_object = self.model.crystal_object[current_image]
        
        if current_layer >= len(crystal_object.growth_lines):
            return
        
        points = crystal_object.growth_lines[current_layer]
        if self.point_index1 >= len(points) or self.point_index2 >= len(points):
            return
        
        p1 = points[self.point_index1]
        p2 = points[self.point_index2]
        
        from PySide2.QtCore import QPointF
        middle_point = QPointF((p1.x() + p2.x()) / 2, (p1.y() + p2.y()) / 2)
        
        insert_index = max(self.point_index1, self.point_index2)
        crystal_object.growth_lines[current_layer].insert(insert_index, middle_point)
        
        if self.update_callback:
            self.update_callback()


class InsertGridLinePointBetweenCommand(CrystalCommand):
    
    def __init__(self, model, line_index, point_index1, point_index2, update_callback=None):
        super().__init__(model, update_callback)
        self.line_index = line_index
        self.point_index1 = point_index1
        self.point_index2 = point_index2
    
    def execute(self):
        self._save_state()
        current_image = self.model.crystal_object[self.model.current_image]
        
        if self.line_index >= len(current_image.grid_lines):
            return
        
        points = current_image.grid_lines[self.line_index]
        if self.point_index1 >= len(points) or self.point_index2 >= len(points):
            return
        
        p1 = points[self.point_index1]
        p2 = points[self.point_index2]
        
        from PySide2.QtCore import QPointF
        middle_point = QPointF((p1.x() + p2.x()) / 2, (p1.y() + p2.y()) / 2)
        
        insert_index = max(self.point_index1, self.point_index2)
        current_image.grid_lines[self.line_index].insert(insert_index, middle_point)
        
        if self.update_callback:
            self.update_callback()
