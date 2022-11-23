class Action(object):
    def __init__(self, from_version, to_version):
        self.from_version = from_version
        self.to_version = to_version

    def apply(self):
        pass


class InsertAction(Action):
    def __init__(self, pos, text, from_version, to_version):
        super().__init__(from_version, to_version)
        self.pos = pos
        self.text = text


class ReplaceAction(Action):
    def __init__(self, pos, text, from_version, to_version):
        super().__init__(from_version, to_version)
        self.pos = pos
        self.text = text


class DeleteAction(Action):
    def __init__(self, pos, length, from_version, to_version):
        super().__init__(from_version, to_version)
        self.pos = pos
        self.length = length


class TextHistory(object):
    def __init__(self):
        self._text = ""
        self._version = 0
        self._actions = []

    @property
    def version(self):
        return self._version

    @property
    def text(self):
        return self._text

    def insert(self, text: str, pos=None):
        if pos == 0:
            self._text = text + self._text
        elif pos:
            if 0 < pos <= len(self._text):
                self._text = self._text[:pos] + text + self._text[pos:]
            else:
                raise ValueError("Указана недопустимая позиция")
        else:
            pos = len(self._text)
            self._text += text
        action = InsertAction(pos, text, self._version, self._version + 1)
        self._actions.append([self._version, action])
        self._version += 1
        return self._version

    def replace(self, text: str, pos=None):
        if pos == 0:
            self._text = text
        elif pos:
            if 0 < pos <= len(self._text):
                start_text = self._text[:pos]
                end_text = self._text[pos + len(text):]
                self._text = f"{start_text}{text}{end_text}"
            else:
                raise ValueError("Указана недопустимая позиция")
        else:
            pos = len(self._text)
            self._text += text
        action = ReplaceAction(pos, text, self._version, self._version + 1)
        self._actions.append([self._version, action])
        self._version += 1
        return self._version

    def delete(self, pos: int, length: int):
        if pos == 0:
            self._text = self._text[pos + length:]
        elif 0 < pos < len(self._text) and length + pos < len(self._text):
            self._text = self._text[:pos] + self._text[pos + length:]
        else:
            raise ValueError("Указана недопустимая позиция")
        action = DeleteAction(pos, length, self._version, self._version + 1)
        self._actions.append([self._version, action])
        self._version += 1
        return self._version

    def action(self, action: Action):
        if (action.from_version == self._version and
                action.to_version > self._version):
            if type(action) is InsertAction:
                self.insert(action.text, action.pos)
            elif type(action) is ReplaceAction:
                self.replace(action.text, action.pos)
            elif type(action) is DeleteAction:
                self.delete(action.pos, action.length)
            else:
                raise TypeError("Указан недопустимый тип действия")
            self._version = action.to_version
        else:
            raise ValueError("Указана недопустимая версия")
        return self._version

    def get_actions(self, from_version=0, to_version=None):
        if to_version is None:
            if len(self._actions) == 0:
                to_version = 0
            else:
                to_version = len(self._actions) - 1
        if from_version == 0 and to_version == 0:
            return []
        if (self._actions[-1][0] < to_version or
                self._actions[0][0] > from_version or
                from_version > to_version):
            raise ValueError("Указана недопустимая версия")
        return self.optimize_actions(from_version, to_version)

    def optimize_actions(self, from_version, to_version):
        prev_action = None
        result = []
        for version, action in self._actions:
            if from_version <= version <= to_version:
                if type(prev_action) is type(action):
                    is_optimized = False
                    if (type(action) is InsertAction and
                            action.pos == prev_action.pos + 1):
                        action.text = prev_action.text + action.text
                        is_optimized = True
                    elif (type(action) is ReplaceAction and
                          action.pos == prev_action.pos +
                          len(prev_action.text)):
                        action.text = prev_action.text + action.text
                        is_optimized = True
                    elif (type(action) is DeleteAction and
                          action.pos == prev_action.pos):
                        action.length += prev_action.length
                        is_optimized = True
                    else:
                        result.append(action)
                    if is_optimized:
                        action.pos = prev_action.pos
                        action.from_version = prev_action.from_version
                        result[-1] = action
                else:
                    result.append(action)
                prev_action = action
        return result
