import { ActionMenu } from "@primer/react"
import { ActionList } from "@primer/react"


function MyActionMenu() {
    return(
<ActionMenu>
  <ActionMenu.Button>Open menu</ActionMenu.Button>
  <ActionMenu.Overlay>
    <ActionList>
      <ActionList.Item
        onSelect={() => {
          alert('Item one clicked')
        }}
      >
        Item one
      </ActionList.Item>
      <ActionList.Item
        onSelect={() => {
          alert('Item two clicked')
        }}
      >
        Item two
      </ActionList.Item>
      <ActionList.Item
        onSelect={() => {
          alert('Item three clicked')
        }}
      >
        Item three
      </ActionList.Item>
    </ActionList>
  </ActionMenu.Overlay>
</ActionMenu>
)}
export default MyActionMenu;