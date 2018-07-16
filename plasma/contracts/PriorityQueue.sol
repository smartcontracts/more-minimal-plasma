pragma solidity ^0.4.0;

import "./SafeMath.sol";


/**
 * @title PriorityQueue
 * @dev A priority queue implementation.
 */
contract PriorityQueue {
    using SafeMath for uint256;


    /*
     *  Modifiers
     */

    modifier onlyOwner() {
        require(msg.sender == owner);
        _;
    }


    /*
     *  Storage
     */

    address owner;
    QueueItem[] heapList;
    uint256 public currentSize;

    struct QueueItem {
        uint256 priority;
        uint256 value;
    }


    /*
     * Constructor
     */

    constructor() public {
        owner = msg.sender;
        heapList.push(QueueItem({
            priority: 0,
            value: 0
        }));
        currentSize = 0;
    }


    /*
     * Public functions
     */

    function insert(uint256 priority, uint256 value) public onlyOwner {
        heapList.push(QueueItem({
            priority: priority,
            value: value
        }));
        currentSize = currentSize.add(1);
        percUp(currentSize);
    }

    function delMin() public onlyOwner returns (uint256, uint256) {
        QueueItem memory retItem = heapList[1];
        replaceItem(1, heapList[currentSize]);
        delete heapList[currentSize];
        currentSize = currentSize.sub(1);
        percDown(1);
        heapList.length = heapList.length.sub(1);
        return (retItem.priority, retItem.value);
    }

    function minChild(uint256 i) public view returns (uint256) {
        if (i.mul(2).add(1) > currentSize) {
            return i.mul(2);
        } else {
            if (heapList[i.mul(2)].priority < heapList[i.mul(2).add(1)].priority) {
                return i.mul(2);
            } else {
                return i.mul(2).add(1);
            }
        }
    }

    function getMin() public view returns (uint256, uint256) {
        return (heapList[1].priority, heapList[1].value);
    }


    /*
     * Private functions
     */

    function percUp(uint256 _i) private {
        uint256 i = _i;
        uint256 j = i;
        QueueItem memory newVal = heapList[i];
        while (newVal.priority < heapList[i.div(2)].priority) {
            replaceItem(i, heapList[i.div(2)]);
            i = i.div(2);
        }
        if (i != j) {
            replaceItem(i, newVal);
        }
    }

    function percDown(uint256 _i) private {
        uint256 i = _i;
        uint256 j = i;
        QueueItem memory newVal = heapList[i];
        uint256 mc = minChild(i);
        while (mc <= currentSize && newVal.priority > heapList[mc].priority) {
            replaceItem(i, heapList[mc]);
            i = mc;
            mc = minChild(i);
        }
        if (i != j) {
            replaceItem(i, newVal);
        }
    }

    function replaceItem(uint256 _i, QueueItem memory _item) private {
        heapList[_i] = QueueItem({
            priority: _item.priority,
            value: _item.value
        });
    }
}
