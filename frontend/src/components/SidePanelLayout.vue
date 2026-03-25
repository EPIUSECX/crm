<template>
  <div class="sections flex flex-col overflow-y-auto">
    <template v-for="(section, i) in _sections" :key="section.name">
      <div v-if="section.visible" class="section flex flex-col">
        <div
          v-if="i !== firstVisibleIndex()"
          class="w-full section-border h-px border-t"
        />
        <div class="p-1 sm:p-3">
          <CollapsibleSection
            labelClass="px-2 font-semibold"
            headerClass="h-8"
            :label="section.label"
            :hideLabel="!section.label"
            :opened="section.opened"
          >
            <template #header="{ opened, toggle }">
              <div
                v-if="!section.hideLabel"
                class="section-header flex h-8 items-center justify-between"
              >
                <div
                  class="flex max-w-fit cursor-pointer items-center gap-2 px-2 text-base font-semibold text-ink-gray-9"
                  @click="toggle"
                >
                  <FeatherIcon
                    name="chevron-right"
                    class="h-4 transition-all duration-300 ease-in-out"
                    :class="{ 'rotate-90': opened }"
                  />
                  <div
                    v-if="section.icon"
                    class="flex h-6 w-6 items-center justify-center rounded bg-surface-gray-3 text-ink-gray-7"
                  >
                    <Icon :icon="section.icon" class="h-3.5 w-3.5" />
                  </div>
                  <span>
                    {{ __(section.label) || __('Untitled') }}
                  </span>
                </div>
                <div class="flex items-center">
                  <slot name="actions" v-bind="{ section }">
                    <Button
                      v-if="!preview && section.showEditButton"
                      variant="ghost"
                      class="mr-2 w-7"
                      :icon="EditIcon"
                      @click="showSidePanelModal = true"
                    />
                  </slot>
                </div>
              </div>
            </template>
            <slot v-bind="{ section }">
              <FadedScrollableDiv
                v-if="section.columns?.[0].fields.length"
                class="column flex flex-col gap-1.5 overflow-y-auto"
              >
                <template
                  v-for="field in section.columns[0].fields || []"
                  :key="field.fieldname"
                >
                  <div
                    v-if="field.visible"
                    class="field px-3 leading-5 first:mt-3"
                    :class="
                      isWideField(field)
                        ? 'flex flex-col gap-2 py-2'
                        : 'flex items-center gap-2'
                    "
                  >
                    <template v-if="isWideField(field)">
                      <div class="flex items-center gap-2">
                        <div
                          v-if="getFieldIcon(field)"
                          class="flex h-6 w-6 shrink-0 items-center justify-center rounded bg-surface-gray-3 text-ink-gray-7"
                        >
                          <Icon :icon="getFieldIcon(field)" class="h-3.5 w-3.5" />
                        </div>
                        <div class="flex min-w-0 items-center gap-1">
                          <div class="truncate text-sm text-ink-gray-5">
                            {{ __(field.label) }}
                          </div>
                          <div
                            v-if="
                              field.reqd ||
                              (field.mandatory_depends_on &&
                                field.mandatory_via_depends_on)
                            "
                            class="text-ink-red-2"
                          >
                            *
                          </div>
                        </div>
                      </div>
                      <div class="wide-field-content w-full overflow-hidden">
                        <Grid
                          v-if="field.fieldtype === 'Table'"
                          v-model="doc[field.fieldname]"
                          v-model:parent="doc"
                          compact
                          :label="''"
                          :doctype="field.options"
                          :parentDoctype="doctype"
                          :parentFieldname="field.fieldname"
                        />
                        <TableMultiselectInput
                          v-else-if="field.fieldtype === 'Table MultiSelect'"
                          v-model="doc[field.fieldname]"
                          :doctype="field.options"
                          @change="(value) => fieldChange(value, field)"
                        />
                        <FileUploader
                          v-else-if="['Attach', 'Attach Image'].includes(field.fieldtype)"
                          :validateFile="
                            field.fieldtype === 'Attach Image'
                              ? validateIsImageFile
                              : undefined
                          "
                          @success="(file) => fieldChange(file.file_url, field)"
                        >
                          <template #default="{ progress, uploading, openFileSelector }">
                            <div class="flex flex-col gap-3">
                              <div
                                v-if="
                                  field.fieldtype === 'Attach Image' &&
                                  doc[field.fieldname]
                                "
                                class="overflow-hidden rounded-lg border border-outline-gray-modals bg-surface-white"
                              >
                                <img
                                  :src="doc[field.fieldname]"
                                  :alt="field.label"
                                  class="h-40 w-full object-cover"
                                />
                              </div>
                              <div
                                v-else-if="doc[field.fieldname]"
                                class="flex items-center justify-between gap-3 rounded-lg border border-outline-gray-modals bg-surface-white px-3 py-2"
                              >
                                <button
                                  class="truncate text-left text-sm text-ink-gray-8 hover:text-ink-gray-9"
                                  @click="openFile(doc[field.fieldname])"
                                >
                                  {{ getFileName(doc[field.fieldname]) }}
                                </button>
                                <Button
                                  variant="ghost"
                                  icon="external-link"
                                  @click="openFile(doc[field.fieldname])"
                                />
                              </div>
                              <div class="flex flex-wrap gap-2">
                                <Button
                                  :label="
                                    uploading
                                      ? __('Uploading {0}%', [progress])
                                      : doc[field.fieldname]
                                        ? __('Change File')
                                        : field.fieldtype === 'Attach Image'
                                          ? __('Upload Image')
                                          : __('Upload File')
                                  "
                                  :iconLeft="
                                    field.fieldtype === 'Attach Image'
                                      ? 'image'
                                      : 'paperclip'
                                  "
                                  @click="openFileSelector"
                                />
                                <Button
                                  v-if="doc[field.fieldname]"
                                  :label="__('Open')"
                                  variant="outline"
                                  iconLeft="external-link"
                                  @click="openFile(doc[field.fieldname])"
                                />
                                <Button
                                  v-if="doc[field.fieldname]"
                                  :label="__('Remove')"
                                  variant="outline"
                                  theme="red"
                                  iconLeft="trash-2"
                                  @click="fieldChange('', field)"
                                />
                              </div>
                            </div>
                          </template>
                        </FileUploader>
                      </div>
                    </template>
                    <template v-else>
                      <Tooltip :text="__(field.label)" :hoverDelay="1">
                        <div
                          class="w-[35%] min-w-20 shrink-0 flex items-center gap-0.5"
                        >
                          <div class="truncate text-sm text-ink-gray-5">
                            {{ __(field.label) }}
                          </div>
                          <div
                            v-if="
                              field.reqd ||
                              (field.mandatory_depends_on &&
                                field.mandatory_via_depends_on)
                            "
                            class="text-ink-red-2"
                          >
                            *
                          </div>
                        </div>
                      </Tooltip>
                      <div class="flex items-center justify-between w-[65%]">
                      <div
                        class="grid min-h-[28px] flex-1 items-center overflow-hidden text-base"
                      >
                        <div
                          v-if="
                            field.read_only &&
                            ![
                              'Int',
                              'Float',
                              'Currency',
                              'Percent',
                              'Check',
                              'Dropdown',
                            ].includes(field.fieldtype)
                          "
                          class="flex h-7 cursor-pointer items-center px-2 py-1 text-ink-gray-5"
                        >
                          <Tooltip :text="__(field.tooltip)">
                            <div>{{ doc[field.fieldname] }}</div>
                          </Tooltip>
                        </div>
                        <PrimaryDropdown
                          v-else-if="field.fieldtype === 'Dropdown'"
                          :value="doc[field.fieldname]"
                          :placeholder="field.placeholder"
                          :options="field.options"
                          :create="field.create"
                          :label="field.label"
                        />
                        <FormControl
                          v-else-if="field.fieldtype == 'Check'"
                          v-model="doc[field.fieldname]"
                          class="form-control"
                          type="checkbox"
                          :disabled="Boolean(field.read_only)"
                          @change.stop="
                            fieldChange($event.target.checked, field)
                          "
                        />
                        <FormControl
                          v-else-if="
                            [
                              'Small Text',
                              'Text',
                              'Long Text',
                              'Code',
                            ].includes(field.fieldtype)
                          "
                          class="form-control"
                          type="textarea"
                          :value="doc[field.fieldname]"
                          :placeholder="field.placeholder"
                          :debounce="500"
                          @change.stop="fieldChange($event.target.value, field)"
                        />
                        <FormControl
                          v-else-if="field.fieldtype === 'Select'"
                          v-model="doc[field.fieldname]"
                          class="form-control cursor-pointer [&_select]:cursor-pointer truncate [&>*]:!ring-0"
                          type="select"
                          :options="field.options"
                          :placeholder="field.placeholder"
                          @update:modelValue="(v) => fieldChange(v, field)"
                        />
                        <Link
                          v-else-if="field.fieldtype === 'User'"
                          class="form-control"
                          :value="
                            doc[field.fieldname] &&
                            getUser(doc[field.fieldname]).full_name
                          "
                          doctype="User"
                          :filters="field.filters"
                          :placeholder="
                            __('Select') + ' ' + field.label + '...'
                          "
                          :hideMe="true"
                          @change="(v) => fieldChange(v, field)"
                        >
                          <template v-if="doc[field.fieldname]" #prefix>
                            <UserAvatar
                              class="mr-1.5"
                              :user="doc[field.fieldname]"
                              size="sm"
                            />
                          </template>
                          <template #item-prefix="{ option }">
                            <UserAvatar
                              class="mr-1.5"
                              :user="option.value"
                              size="sm"
                            />
                          </template>
                          <template #item-label="{ option }">
                            <Tooltip :text="option.value">
                              <div class="cursor-pointer">
                                {{ getUser(option.value).full_name }}
                              </div>
                            </Tooltip>
                          </template>
                        </Link>
                        <Link
                          v-else-if="
                            ['Link', 'Dynamic Link'].includes(field.fieldtype)
                          "
                          class="form-control select-text"
                          :value="doc[field.fieldname]"
                          :doctype="
                            field.fieldtype == 'Link'
                              ? field.options
                              : doc[field.options]
                          "
                          :filters="field.filters"
                          :placeholder="field.placeholder"
                          :onCreate="field.create"
                          @change="(v) => fieldChange(v, field)"
                        />
                        <div
                          v-else-if="field.fieldtype === 'Time'"
                          class="form-control"
                        >
                          <TimePicker
                            :value="doc[field.fieldname]"
                            :format="getFormat('', '', false, true, false)"
                            :placeholder="field.placeholder"
                            @change="(v) => fieldChange(v, field)"
                          />
                        </div>
                        <div
                          v-else-if="field.fieldtype === 'Datetime'"
                          class="form-control"
                        >
                          <DateTimePicker
                            :value="doc[field.fieldname]"
                            :format="getFormat('', '', true, true, false)"
                            :placeholder="field.placeholder"
                            placement="left-start"
                            @change="(v) => fieldChange(v, field)"
                          />
                        </div>
                        <div
                          v-else-if="field.fieldtype === 'Date'"
                          class="form-control"
                        >
                          <DatePicker
                            :value="doc[field.fieldname]"
                            :format="getFormat('', '', true, false, false)"
                            :placeholder="field.placeholder"
                            placement="left-start"
                            @change="(v) => fieldChange(v, field)"
                          />
                        </div>
                        <FormattedInput
                          v-else-if="field.fieldtype === 'Percent'"
                          class="form-control"
                          type="text"
                          :value="getFormattedPercent(field.fieldname, doc)"
                          :placeholder="field.placeholder"
                          :debounce="500"
                          :disabled="Boolean(field.read_only)"
                          @change.stop="
                            fieldChange(flt($event.target.value), field)
                          "
                        />
                        <Password
                          v-else-if="field.fieldtype === 'Password'"
                          class="form-control"
                          :value="doc[field.fieldname]"
                          :placeholder="field.placeholder"
                          :debounce="500"
                          :disabled="Boolean(field.read_only)"
                          @change.stop="fieldChange($event.target.value, field)"
                        />
                        <FormattedInput
                          v-else-if="field.fieldtype === 'Int'"
                          class="form-control"
                          type="text"
                          :value="doc[field.fieldname] || '0'"
                          :placeholder="field.placeholder"
                          :debounce="500"
                          :disabled="Boolean(field.read_only)"
                          @change.stop="fieldChange($event.target.value, field)"
                        />
                        <FormattedInput
                          v-else-if="field.fieldtype === 'Float'"
                          class="form-control"
                          type="text"
                          :value="getFormattedFloat(field.fieldname, doc)"
                          :placeholder="field.placeholder"
                          :debounce="500"
                          :disabled="Boolean(field.read_only)"
                          @change.stop="
                            fieldChange(flt($event.target.value), field)
                          "
                        />
                        <FormattedInput
                          v-else-if="field.fieldtype === 'Currency'"
                          class="form-control"
                          type="text"
                          :value="getFormattedCurrency(field.fieldname, doc)"
                          :placeholder="field.placeholder"
                          :debounce="500"
                          :disabled="Boolean(field.read_only)"
                          @change.stop="
                            fieldChange(flt($event.target.value), field)
                          "
                        />
                        <FormControl
                          v-else
                          class="form-control"
                          type="text"
                          :value="doc[field.fieldname]"
                          :placeholder="field.placeholder"
                          :debounce="500"
                          @change.stop="fieldChange($event.target.value, field)"
                        />
                      </div>
                      <div class="ml-1">
                        <ArrowUpRightIcon
                          v-if="
                            field.fieldtype === 'Link' &&
                            field.link &&
                            doc[field.fieldname]
                          "
                          class="h-4 w-4 shrink-0 cursor-pointer text-ink-gray-5 hover:text-ink-gray-8"
                          @click.stop="field.link(doc[field.fieldname])"
                        />
                        <EditIcon
                          v-if="
                            field.fieldtype === 'Link' &&
                            field.edit &&
                            doc[field.fieldname]
                          "
                          class="size-3.5 shrink-0 cursor-pointer text-ink-gray-5 hover:text-ink-gray-8"
                          @click.stop="field.edit(doc[field.fieldname])"
                        />
                      </div>
                    </div>
                    </template>
                  </div>
                </template>
              </FadedScrollableDiv>
            </slot>
          </CollapsibleSection>
        </div>
      </div>
    </template>
  </div>
  <SidePanelModal
    v-if="showSidePanelModal"
    v-model="showSidePanelModal"
    :doctype="doctype"
    @reload="() => emit('reload')"
  />
</template>

<script setup>
import Password from '@/components/Controls/Password.vue'
import FormattedInput from '@/components/Controls/FormattedInput.vue'
import CollapsibleSection from '@/components/CollapsibleSection.vue'
import PrimaryDropdown from '@/components/PrimaryDropdown.vue'
import FadedScrollableDiv from '@/components/FadedScrollableDiv.vue'
import ArrowUpRightIcon from '@/components/Icons/ArrowUpRightIcon.vue'
import EditIcon from '@/components/Icons/EditIcon.vue'
import Link from '@/components/Controls/Link.vue'
import Grid from '@/components/Controls/Grid.vue'
import TableMultiselectInput from '@/components/Controls/TableMultiselectInput.vue'
import UserAvatar from '@/components/UserAvatar.vue'
import SidePanelModal from '@/components/Modals/SidePanelModal.vue'
import Icon from '@/components/Icon.vue'
import { getMeta } from '@/stores/meta'
import { usersStore } from '@/stores/users'
import { isMobileView } from '@/composables/settings'
import { getFormat, evaluateDependsOnValue, validateIsImageFile } from '@/utils'
import { flt } from '@/utils/numberFormat.js'
import { Tooltip, DateTimePicker, DatePicker, TimePicker, FileUploader } from 'frappe-ui'
import { useDocument } from '@/data/document'
import { ref, computed, getCurrentInstance, provide } from 'vue'

const props = defineProps({
  sections: { type: Object, default: () => ({}) },
  doctype: { type: String, default: 'CRM Lead' },
  docname: { type: String, required: true },
  preview: { type: Boolean, default: false },
  addContact: { type: Function, default: null },
})

const emit = defineEmits(['beforeFieldChange', 'afterFieldChange', 'reload'])

const { getFormattedPercent, getFormattedFloat, getFormattedCurrency } =
  getMeta(props.doctype)

const { users, isManager, getUser } = usersStore()

const showSidePanelModal = ref(false)

let document = { doc: {} }
let triggerOnChange
let triggerOnRowAdd
let triggerOnRowRemove

if (props.docname) {
  let d = useDocument(props.doctype, props.docname)
  document = d.document
  triggerOnChange = d.triggerOnChange
  triggerOnRowAdd = d.triggerOnRowAdd
  triggerOnRowRemove = d.triggerOnRowRemove
}

const doc = computed(() => document.doc || {})

provide('triggerOnChange', async (fieldname, value, row) => {
  await triggerOnChange?.(fieldname, value, row)
  if (!props.preview) {
    document.save.submit(null, {
      onSuccess: () => emit('afterFieldChange', { [fieldname]: value }),
    })
  }
})

provide('triggerOnRowAdd', async (row) => {
  await triggerOnRowAdd?.(row)
  if (!props.preview) {
    document.save.submit(null, {
      onSuccess: () =>
        emit('afterFieldChange', { [row.parentfield]: doc.value[row.parentfield] }),
    })
  }
})

provide('triggerOnRowRemove', async (selectedRows, rows) => {
  await triggerOnRowRemove?.(selectedRows, rows)
  if (!props.preview) {
    const parentfield = rows?.[0]?.parentfield
    document.save.submit(null, {
      onSuccess: () =>
        emit('afterFieldChange', { [parentfield || 'rows']: rows }),
    })
  }
})

const _sections = computed(() => {
  if (!props.sections?.length) return []
  let editButtonAdded = false
  return props.sections.map((section) => {
    if (section.columns?.length) {
      section.columns[0].fields = section.columns[0].fields.map((field) => {
        return parsedField(field)
      })
    }
    let _section = parsedSection(section, editButtonAdded)
    if (_section.showEditButton) {
      editButtonAdded = true
    }
    return _section
  })
})

function parsedField(field) {
  if (field.fieldtype == 'Select' && typeof field.options === 'string') {
    field.options = field.options.split('\n').map((option) => {
      return { label: option, value: option }
    })

    if (field.options[0].value !== '') {
      field.options.unshift({ label: '', value: '' })
    }
  }

  if (field.fieldtype === 'Link' && field.options === 'User') {
    field.fieldtype = 'User'
    field.link_filters = JSON.stringify({
      ...(field.link_filters ? JSON.parse(field.link_filters) : {}),
      name: ['in', users.data?.crmUsers?.map((user) => user.name)],
      ignore_user_type: 1,
    })
  }

  const read_only_via_depends_on = evaluateDependsOnValue(
    field.read_only_depends_on,
    doc.value,
  )

  let _field = {
    ...field,
    filters: field.link_filters && JSON.parse(field.link_filters),
    placeholder: field.placeholder || field.label,
    display_via_depends_on: evaluateDependsOnValue(field.depends_on, doc.value),
    mandatory_via_depends_on: evaluateDependsOnValue(
      field.mandatory_depends_on,
      doc.value,
    ),
    read_only:
      field.read_only ||
      (field.read_only_depends_on && read_only_via_depends_on),
  }

  _field.visible = isFieldVisible(_field)
  return _field
}

const instance = getCurrentInstance()
const attrs = instance?.vnode?.props ?? {}

async function fieldChange(value, df) {
  if (props.preview) return

  await triggerOnChange(df.fieldname, value)

  const hasListener = attrs['onBeforeFieldChange'] !== undefined

  if (hasListener) {
    emit('beforeFieldChange', { [df.fieldname]: value })
  } else {
    document.save.submit(null, {
      onSuccess: () => emit('afterFieldChange', { [df.fieldname]: value }),
    })
  }
}

function parsedSection(section, editButtonAdded) {
  let isContactSection = section.name == 'contacts_section'
  section.showEditButton = !(
    isMobileView.value ||
    !isManager() ||
    isContactSection ||
    editButtonAdded
  )

  section.icon = getSectionIcon(section)
  section.visible =
    isContactSection ||
    section.columns?.[0].fields.filter((f) => f.visible).length

  return section
}

function getSectionIcon(section) {
  const labels = section.columns?.[0]?.fields
    ?.filter((field) => field.visible)
    .map((field) => `${field.label || ''} ${field.fieldname || ''}`.toLowerCase())

  if (!labels?.length) return 'grid'
  if (section.columns?.[0]?.fields?.some((field) => field.fieldtype === 'Attach Image')) {
    return null
  }
  if (section.columns?.[0]?.fields?.some((field) => field.fieldtype === 'Attach')) {
    return null
  }
  if (labels.some((label) => label.includes('tag'))) {
    return 'tag'
  }
  if (section.columns?.[0]?.fields?.some((field) => field.fieldtype === 'Table')) {
    return 'grid'
  }
  if (
    section.columns?.[0]?.fields?.some(
      (field) => field.fieldtype === 'Table MultiSelect',
    )
  ) {
    return 'tag'
  }
  return 'grid'
}

function getFieldIcon(field) {
  if (field.fieldtype === 'Attach Image') return null
  if (field.fieldtype === 'Attach') return null

  if (field.fieldtype === 'Table') {
    const label = `${field.label || ''} ${field.fieldname || ''}`.toLowerCase()
    if (
      label.includes('document') ||
      label.includes('file') ||
      label.includes('attach')
    ) {
      return null
    }
    return 'grid'
  }

  if (field.fieldtype === 'Table MultiSelect') return 'tag'

  return 'grid'
}

function isWideField(field) {
  return ['Table', 'Table MultiSelect', 'Attach', 'Attach Image'].includes(
    field.fieldtype,
  )
}

function getFileName(url) {
  if (!url) return ''
  return url.split('/').pop()?.split('?')[0] || url
}

function openFile(url) {
  if (!url) return
  window.open(url, '_blank', 'noopener')
}

function isFieldVisible(field) {
  if (props.preview) return true

  const hideEmptyReadOnly = Number(
    window.sysdefaults?.hide_empty_read_only_fields ?? 1,
  )

  const shouldShowReadOnly =
    field.read_only && (doc.value?.[field.fieldname] || !hideEmptyReadOnly)

  return (
    (field.fieldtype == 'Check' || shouldShowReadOnly || !field.read_only) &&
    (!field.depends_on || field.display_via_depends_on) &&
    !field.hidden
  )
}

function firstVisibleIndex() {
  return _sections.value.findIndex((section) => section.visible)
}
</script>

<style scoped>
.form-control {
  margin: 2px;
}

:deep(.form-control input:not([type='checkbox'])),
:deep(.form-control select),
:deep(.form-control textarea),
:deep(.form-control button),
.dropdown-button {
  border-color: transparent;
  background: transparent;
}

:deep(.form-control button) {
  gap: 0;
}
:deep(.form-control [type='checkbox']) {
  margin-left: 9px;
  cursor: pointer;
}

:deep(.form-control button > div) {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

:deep(.form-control button svg) {
  color: white;
  width: 0;
}

.sections .section .column {
  max-height: 300px;
}
.sections .section:last-of-type .column {
  max-height: none;
}

.wide-field-content {
  min-width: 0;
}

:deep(.wide-field-content .combobox button),
:deep(.wide-field-content .form-control button) {
  color: inherit;
}
</style>
