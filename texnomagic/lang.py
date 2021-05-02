"""
TexnoMagic Language grammar and parsing
"""
from parsimonious.grammar import Grammar
from parsimonious.nodes import NodeVisitor


# Parsing Expression Grammar (PEG) for TexnoMagic Language
TEXNO_MAGIC_GRAMMAR = """
spell = spell_bolt / spell_ball / spell_beam / spell_area / spell_cone / spell_self / spell_shield / spell_blink


spell_bolt = modable_effect bolt_mods "bolt" dir

spell_ball = modable_effect bolt_mods "ball" dir

spell_beam = modable_effect bolt_mods "beam" dir

spell_cone = modable_effect area_mods "cone" dir

spell_area = modable_effect area_mods "area"

spell_self = modable_effect "self"

spell_shield = modable_effect "shield" shield_shape

spell_blink = "air" ws "lightning" dir


modable_effect = effect_mods effect
effect = (element ws)+
element = "fire" / "ice" / "water" / "air" / "lightning" / "earth" / "life" / "death" / "magic"

area_mod = mod_size
area_mods = (area_mod ws)*
bolt_mod = mod_size / mod_speed / mod_homing
bolt_mods = (bolt_mod ws)*
effect_mod = mod_size / mod_speed
effect_mods = (effect_mod ws)*

mod_size = "big" / "small"
mod_speed = "fast" / "slow"
mod_homing = "homing"

dir = (ws direction)?
direction = "forward" / "enemy" / "friend" / "random"

shield_shape = (ws ("area" / "cone" / "self"))?


ws = " "+
"""


class TexnoMagicLanguage:
    def __init__(self):
        self.grammar = Grammar(TEXNO_MAGIC_GRAMMAR)

    def parse(self, text):
        """
        use this to parse TexnoMagic spell into its data representation
        """
        tree = self.grammar.parse(text)
        v = TexnoVisitor()
        output = v.visit(tree)
        return output


class TexnoVisitor(NodeVisitor):
    def visit_element(self, node, vc):
        return node.text

    def visit_effect(self, node, vc):
        elems = [e[0] for e in vc]
        return elems

    def visit_direction(self, node, vc):
        return node.text

    def visit_dir(self, node, vc):
        if vc:
            return vc[0][1]
        return 'default'

    def visit_mod_size(self, node, vc):
        if vc[0].text == 'small':
            v = 0.5
        else:  # big
            v = 2
        d = {'size': v}
        return d

    def visit_mod_speed(self, node, vc):
        if vc[0].text == 'slow':
            v = 0.5
        else:  # fast
            v = 2
        d = {'speed': v}
        return d

    def visit_mod_homing(self, node, vc):
        d = {'homing': 1}
        return d

    def visit_bolt_mod(self, node, vc):
        return vc[0]

    def visit_area_mod(self, node, vc):
        return vc[0]

    def visit_effect_mod(self, node, vc):
        return vc[0]

    def visit_bolt_mods(self, node, vc):
        mods = [c[0] for c in vc]
        mods = merge_mods(mods)
        d = {
            'spell_mods': mods,
        }
        return d

    def visit_area_mods(self, node, vc):
        mods = [c[0] for c in vc]
        mods = merge_mods(mods)
        d = {
            'spell_mods': mods,
        }
        return d

    def visit_modable_effect(self, node, vc):
        mods = [c[0] for c in vc[0]]
        mods = merge_mods(mods)
        mfx = {
            'effect': vc[1],
            'effect_mods': mods,
        }
        return mfx

    def visit_shield_shape(self, node, vc):
        shape = 'self'
        if vc:
            shape = vc[0][1][0].text
        return shape

    def visit_spell_bolt(self, node, vc):
        return boltlike_spell('bolt', node, vc)

    def visit_spell_ball(self, node, vc):
        return boltlike_spell('ball', node, vc)

    def visit_spell_beam(self, node, vc):
        return boltlike_spell('beam', node, vc)

    def visit_spell_cone(self, node, vc):
        return boltlike_spell('cone', node, vc)

    def visit_spell_area(self, node, vc):
        s = {'spell': 'area'}
        s.update(vc[0])
        s.update(vc[1])
        return s

    def visit_spell_self(self, node, vc):
        s = {'spell': 'self'}
        s.update(vc[0])
        return s

    def visit_spell_shield(self, node, vc):
        s = {
            'spell': 'shield',
            'shape': vc[2],
        }
        s.update(vc[0])
        return s

    def visit_spell_blink(self, node, vc):
        s = {
            'spell': 'blink',
            'direction': vc[3],
        }
        return s

    def visit_spell(self, node, vc):
        return vc[0]

    def generic_visit(self, node, vc):
        return vc or node


def boltlike_spell(name, node, vc):
    s = {'spell': name}
    s.update(vc[0])
    s.update(vc[1])
    s['direction'] = vc[3]
    return s


def merge_mods(mods):
    if not mods:
        return mods
    head, *rest = mods
    merged = head.copy()
    for m in rest:
        for key, val in m.items():
            if key in merged:
                merged[key] = merged[key] * val
            else:
                merged[key] = val
    return merged
