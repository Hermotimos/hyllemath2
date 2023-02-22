import re
from typing import List

from django import template
from django.conf import settings
from django.db.models import Q
from django.template.defaultfilters import linebreaksbr
from django.template.defaulttags import GroupedResult
from django.utils.html import format_html
from django.utils.safestring import mark_safe


register = template.Library()


@register.filter
def ordered_columns(list_: list, n: int) -> List[list]:
    """Sort in one list (used in Toponomikon Index)."""
    try:
        n = int(n)
        list_ = list(list_)
    except (ValueError, TypeError):
        return [list_]
    list_len = len(list_)
    split = list_len // n
    if list_len % n != 0:
        split += 1
    res = []
    for i in range(split + 1):
        if list_[0:split]:
            res.append(list_[0:split])
            list_ = list_[split:]
    return res


@register.filter
def max_synergy_level_no(synergy_levels):

    def max_skill_level_no(skill_levels):
        return max(
            [skill_lvl.level for skill_lvl in skill_levels])

    return max(
        [max_skill_level_no(synergy_lvl.skill_levels.all())
         for synergy_lvl in synergy_levels]
    )


@register.filter
def get_model_name(obj):
    return obj.__class__.__name__


@register.filter
def get_main_audio_path(obj):
    try:
        if obj.audio_set.main_audio:
            return obj.audio_set.main_audio.path
        else:
            return get_main_audio_path(obj.in_location)
    except AttributeError:
        return None


@register.filter
def get_audio_set(obj):
    try:
        if obj.audio_set:
            return obj.audio_set
        else:
            return get_audio_set(obj.in_location)
    except AttributeError:
        return None


@register.filter
def format_as_html(text):
    text = format_html(text)
    return mark_safe(text)


@register.filter
def replace(obj_as_text, from_to):
    """Parameter 'from_to' like '&__and' to replace '&' to 'and'."""
    from_ = from_to.split('__')[0]
    to = from_to.split('__')[1]
    return format_as_html(obj_as_text.replace(from_, to))


@register.filter
def brackets_br(text):
    """Add <br> before "(" to move text in brackets to next line."""
    if "(" in text:
        index = text.index("(")
        pre, post = text[:index], text[index:]
        return format_as_html(f"{pre}<br>{post}")
    return text


@register.filter
def game_participants(obj):
    participants = set()
    for game_event in obj.game_events.all():
        for profile in game_event.participants.all():
            if profile.status == 'player':
                participants.add(profile)
    return participants


@register.filter
def pictureset_pictures_in_custom_order(picture_set):

    def get_dimensions_ratio(img):
        return img.width / img.height

    pics = [pic for pic in picture_set.pictures.all()]
    try:
        pics_sorted = sorted(pics, key=lambda pic: get_dimensions_ratio(pic.image.image))

        # sort pictures according to custom cases considering WIDTH:HEIGHT ratio:
        if len(pics) == 2:
            # Put the wider pic on the left / but keep order if width is equal
            # This enables order control by picture names
            if pics_sorted[0].image.image.width == pics_sorted[1].image.image.width:
                return pics_sorted
            return [pics_sorted[1], pics_sorted[0]]
        if len(pics) == 3:
            # Put the widest pic in the middle
            return [pics_sorted[0], pics_sorted[2], pics_sorted[1]]
        # case N
        elif len(pics) == 4:
            return [pics_sorted[0], pics_sorted[2], pics_sorted[3], pics_sorted[1]]
        # default
        else:
            return pics_sorted

    except FileNotFoundError:
        return pics


@register.filter
def players_names_bold(django_filter_html, current_profile):
    from users.models import Profile
    html = str(django_filter_html)
    for pid in Profile.players.values_list('id', flat=True):
        if not (current_profile.id in [82, 93] and pid == 18):
            html = html.replace(
                f'option value="{pid}"',
                f'option value="{pid}" style="font-weight: 600;"')
    return mark_safe(html)


@register.filter
def get_selected(bound_field):
    return bound_field.initial


@register.filter
def render_option(field_choice, selected_objs):
    from communications.models import ThreadTag
    value_obj, label = field_choice
    value = f'value="{value_obj.value}"'
    style = f'style="color: {ThreadTag.objects.get(id=value_obj.value).color};"'
    selected = ''
    if selected_objs:
        selected_ids = [obj.id for obj in selected_objs]
        selected = 'selected=""' if value_obj.value in selected_ids else ''
    return mark_safe(f"<option {value} {style} {selected}>{label}</option>")


@register.filter
def dissect(sth):
    print(type(sth))
    print(sth.__dict__)


@register.filter
def next_elem(list_, current_index):
    """Returns the next element of the list or empty string if there's none."""
    try:
        return list_[int(current_index) + 1]
    except IndexError:
        return ''


@register.filter
def include_silent_participants(results: List[GroupedResult], thread):
    profiles_with_statements = [gr.grouper for gr in results]
    profiles_without_statements = [
        p for p in thread.participants.all()
        if p not in profiles_with_statements]
    results.extend(
        [GroupedResult(grouper=profile, list=[])
         for profile in profiles_without_statements])
    return sorted(results, key=lambda gr_result: gr_result.grouper.character.fullname)


@register.filter
def trim_nums(text: str):
    # Remove level numbers in perks' names (ex. 'Uniki 0.5' -> 'Uniki').
    if text.split('.')[0][-1:] == '0':
        return text.split('.')[0][:-1].strip()
    # Remove level numbers in perks' names (ex. 'Uniki 2' -> 'Uniki').
    if text[-1:] in [str(num) for num in range(0, 10)]:
        return text[:-2]
    return text


@register.filter
def format_conditional_modifier(conditional_modifier, color_class: str):
    text = str(conditional_modifier)
    if "[" in text:
        before, brackets = text.split(sep='[')
        text = before + f'<span class="{color_class}">[{brackets}</span>'

    tooltip = 'data-toggle="tooltip" data-placement="top"'
    combat_types_icons = {
        '/zwar': f'<i class="ra ra-crossed-axes pr-1" {tooltip} title="Walka w zwarciu"></i>',
        '/dyst': f'<i class="ra ra-archery-target pr-1" {tooltip} title="Walka dystansowa"></i>',
        '/wręc': f'<i class="ra ra-hand pr-1" {tooltip} title="Walka wręcz"></i>',
        '/konn': f'<i class="ra ra-horseshoe pr-1" {tooltip} title="Walka konna"></i>',
    }
    if any(k in text for k in combat_types_icons.keys()):
        for abbr, icon in combat_types_icons.items():
            if abbr in text:
                text = icon + text.replace(abbr, "")
    else:
        text = '<i class="ra ra-perspective-dice-two pr-1"></i>' + text

    return mark_safe(text)

#
# @register.filter
# def remove_special_chars(text_or_obj):
#     return "".join(
#         [ch for ch in str(text_or_obj) if ch.lower() in 'abcdefghijklmnopqrstuvwxyz']
#     )
#
#
# @register.filter
# def default_if_emptystring(string, text_if_emtystring):
#     if string == "":
#         return text_if_emtystring
#     return string
#
#
# @register.filter
# def filter_players(informables_qs, current_profile):
#     return informables_qs.filter(
#         character__in=current_profile.character.acquaintances.all())


@register.filter
def kinds_filter(skilltype_kinds_qs, skilltype_kinds_str):
    return any([
        kind in skilltype_kinds_str
        for kind in [kind.name for kind in skilltype_kinds_qs]
    ])


@register.filter
def add_season_img(text):
    static_dir = settings.STATIC_URL
    if text:
        text = text.replace(' dnia', '')
        replacements = {
            'Wiosny': f'<br><img class="img-season" src="{static_dir}img/seasons_spring.png"><br>',
            'Lata': f'<br><img class="img-season" src="{static_dir}img/seasons_summer.png"><br>',
            'Jesieni': f'<br><img class="img-season" src="{static_dir}img/seasons_autumn.png"><br>',
            'Zimy': f'<br><img class="img-season" src="{static_dir}img/seasons_winter.png"><br>',
        }
        cnt = 0
        for k, v in replacements.items():
            cnt += 1 if k in text else 0
            text = text.replace(k, v)
    return mark_safe(text)


@register.filter
def temp_chrono_override(chrono_info: str, profile_id: int):
    # Temporary chronology override for Syngir, Murkon, Dalamar
    if profile_id in [11, 82, 93]:
        for yd in re.findall(r"\s+[0-9]+\s+roku", chrono_info):
            yearnum = int(yd.replace('roku', '').strip())
            if "Nemetha" in chrono_info:
                chrono_info = chrono_info.replace(yd, f" {yearnum+480} roku")
            elif "Enosa" in chrono_info:
                chrono_info = chrono_info.replace(yd, f" {yearnum+444} roku")

        chrono_info = chrono_info.replace(
            "Archonatu Nemetha Samatiana", "Nowej Ery"
        ).replace(
            "Archonatu Enosa Katenoda", "Nowej Ery"
        )

    return mark_safe(chrono_info)


@register.filter
def similar_weapon_types(acquisitions_qs, synergy_lvl):
    weapon_types_with_synergy = [
        a.weapon_type for a in acquisitions_qs.filter(
            ~Q(weapon_type=None), skill_level__level__lte=synergy_lvl)
    ]
    res = "<br><br>"
    for wt in weapon_types_with_synergy:
        comparables = ', '.join([c.name for c in wt.comparables.all()])
        res += f"<b>{wt.name}:</b> {comparables}\n<br>"
    return mark_safe(res)

